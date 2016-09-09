"""
Main command line interface of the pylexibank package.

Like programs such as git, this cli splits its functionality into sub-commands
(see e.g. https://docs.python.org/2/library/argparse.html#sub-commands).
The rationale behind this is that while a lot of different tasks may be
triggered using this cli, most of them require common configuration.

The basic invocation looks like

    lexibank [OPTIONS] <command> [args]

"""
from __future__ import unicode_literals, division, print_function
import os
import sys
from time import time
from textwrap import wrap

from clldutils.clilib import ArgumentParser, ParserError
from clldutils.path import Path
from clldutils import jsonlib
from clldutils import licenses
from pyglottolog.api import Glottolog

import pylexibank
from pylexibank.util import data_path, MarkdownTable
from pylexibank.dataset import Dataset, synonymy_index, TranscriptionReport


HOME = Path(os.path.expanduser('~'))


class ValidationError(ValueError):
    def __init__(self, msg):
        self.msg = msg
        ValueError.__init__(self, msg)


def create(args):
    """Creates a new empty questionaire for a language specified by glottocode.

    lexibank create GLOTTOCODE [SOURCE]
    """
    pass


def is_dataset_dir(d):
    return d.exists() and d.is_dir() \
        and d.name != '_template' and d.joinpath('metadata.json').exists()


def get_dataset(args, name=None):
    name = name or args.args[0]
    dir_ = Path(name)
    if not is_dataset_dir(dir_):
        dir_ = data_path(name, repos=args.lexibank_repos)
        if not is_dataset_dir(dir_):
            raise ParserError('invalid dataset spec')
    return Dataset(dir_)


def download(args):
    """
    Download the raw data for a dataset.

    lexibank download DATASET_ID
    """
    get_dataset(args).download()


def short_title(t, l=40):
    if len(t) > l:
        return wrap(t, width=l)[0] + '...'
    return t


def ls(args):
    """
    lexibank ls [COLS]+

    column specification:
    - license
    - lexemes
    - macroareas
    """
    # FIXME: how to smartly choose columns?
    table = MarkdownTable('ID', 'Title')
    cols = [col for col in args.args if col in ['license', 'lexemes', 'macroareas']]
    tl = 40
    if args.args:
        tl = 25
        table.columns.extend(col.capitalize() for col in cols)
    for d in data_path(repos=Path(args.lexibank_repos)).iterdir():
        if is_dataset_dir(d):
            ds = Dataset(d)
            row = [d.name, short_title(ds.md['dc:title'], l=tl)]
            for col in cols:
                if col == 'license':
                    lic = licenses.find(ds.md.get('dc:license') or '')
                    row.append(lic.id if lic else ds.md.get('dc:license'))
                elif col in ['lexemes', 'macroareas']:
                    mds = list(ds.iter_cldf_metadata())
                    if col == 'lexemes':
                        row.append(sum(md.notes['stats']['lexeme_count'] for md in mds))
                    elif col == 'macroareas':
                        mas = set()
                        for md in mds:
                            mas = mas.union(md.notes['stats']['macroareas'])
                        row.append(', '.join(sorted(mas)))

            table.append(row)
    print(table.render(fmt='simple', sortkey=lambda r: r[0], condensed=False))


def with_dataset(args, func):
    if args.args:
        func(get_dataset(args), **vars(args))
    else:
        for d in sorted(
                data_path(repos=args.lexibank_repos).iterdir(), key=lambda d: d.name):
            if d.is_dir() and d.name != '_template' \
                    and d.joinpath('metadata.json').exists():
                s = time()
                print('processing %s ...' % d.name)
                try:
                    func(get_dataset(args, d.name), **vars(args))
                except NotImplementedError:
                    print('--not implemented--')
                print('... done %s [%.1f secs]' % (d.name, time() - s))


def report(args):
    """
    """
    def _report(ds, **kw):
        ds.report(**kw)

    with_dataset(args, _report)


def cldf(args):
    """
    Create CLDF datasets from the raw data for a dataset.

    lexibank cldf [DATASET_ID]
    """
    # FIXME: get dict of all glottolog langs right here, and attach to datasets!
    languoids = {l.id: l for l in Glottolog(args.glottolog_repos).languoids()}

    def _cldf(ds, **kw):
        ds.glottolog_languoids = languoids
        ds.cldf(**kw)
        ds.write_cognates()

    with_dataset(args, _cldf)


def get_badge(words, name, prop=None, ratio=None):
    prop = prop or name
    if words:
        ratio = len([w for w in words if w.get(prop)]) / float(len(words))
    elif ratio:
        pass
    else:
        ratio = 1.0
    if ratio >= 0.99:
        color = 'brightgreen'
    elif ratio >= 0.9:
        color = 'green'
    elif ratio >= 0.8:
        color = 'yellowgreen'
    elif ratio >= 0.7:
        color = 'yellow'
    elif ratio >= 0.6:
        color = 'orange'
    else:
        color = 'red'
    ratio = int(round(ratio * 100))
    return badge(
        "{0}: {1}%".format(name, ratio), name, '%s%%25' % ratio, color
    )


def badge(title, name, value, color):
    return '![{0}](https://img.shields.io/badge/{1}-{2}-{3}.svg "{0}")'.format(
        title, name, value, color)


def readme(args):
    """Create a README.md file listing the contents of a dataset

    lexibank readme [DATASET_ID]
    """
    with_dataset(args, _readme)


def _readme(ds, **kw):
    #
    # FIXME: write only summary into README.md
    # in case of multiple cldf datasets:
    # - separate lexemes.md and transcriptions.md
    #
    if not list(ds.cldf_dir.glob('*.csv')):
        return
    lines = [
        '# %s' % ds.md.get('dc:title'),
        '',
        'Cite the source dataset as',
        '',
        '> %s' % ds.md.get('dc:bibliographicCitation'),
        '']

    if ds.md.get('dc:license'):
        lines.extend([
            'This dataset is licensed under a %s license' % ds.md.get('dc:license'),
            ''])

    if ds.md.get('dc:identifier'):
        lines.extend([
            'Available online at %s' % ds.md.get('dc:identifier'),
            ''])

    if ds.md.get('dc:related'):
        lines.extend([
            'See also %s' % ds.md.get('dc:related'),
            ''])

    report_by_cldfds = {}
    trlines = []
    rows = []

    totals = [set(), set(), 0, (0, 0)]

    for cldfds in ds.iter_cldf_datasets():
        rows.extend(cldfds.rows)
        stats = cldfds.stats
        sindex, langs = synonymy_index(cldfds)
        if langs:
            sindex /= float(len(langs))
        else:
            sindex = 0
        totals[0] = totals[0].union(langs)
        totals[1] = totals[1].union(stats['parameters'])
        totals[2] += len(cldfds)
        totals[3] = (totals[3][0] + sindex, totals[3][1] + 1)

        report_by_cldfds[cldfds.name] = dict(
            languages=list(langs),
            concepts=list(stats['parameters']),
            lexeme_count=len(cldfds),
            synonymy_index='%.2f' % sindex)

    report_by_cldfds['__total__'] = dict(
        language_count=len(totals[0]),
        concept_count=len(totals[1]),
        lexeme_count=totals[2],
        synonymy_index=totals[3])
    #
    # FIXME: add flags:
    # - cognates
    # - alignments
    # - proto-forms
    #

    tr = TranscriptionReport(ds, ds.dir.joinpath('transcription.json'))
    stats = tr.report['stats']
    badges = [
        get_badge(rows, 'Glottolog', 'Language_ID'),
        get_badge(rows, 'Concepticon', 'Parameter_ID'),
        get_badge(rows, 'Source')
    ]
    if stats['segments']:
        badges.extend([
            get_badge(
                None,
                'LingPy',
                ratio=(stats['segments'] - stats['lingpy_errors']) / stats['segments']),
            get_badge(
                None,
                'CLPA',
                ratio=(stats['segments'] - stats['clpa_errors']) / stats['segments']),
        ])
    lines.extend(['## Statistics', ' '.join(badges), ''])
    stats_lines = [
        '- **Varieties:** {0:,}'.format(len(totals[0])),
        '- **Concepts:** {0:,}'.format(len(totals[1])),
        '- **Lexemes:** {0:,}'.format(totals[2]),
        '- **Synonymy:** %.2f' % (totals[3][0] / totals[3][1]),
        '- **Cognacy:** {0:,} cognates in {1:,} cognate sets'.format(*ds.cognate_stats()),
        '- **Invalid lexemes:** {0:,}'.format(stats['invalid']),
        '- **Tokens:** {0:,}'.format(stats['tokens']),
        '- **Segments:** {0:,} ({1} LingPy errors, {2} CLPA errors, {3} CLPA modified)'
        .format(stats['segments'],
                stats['lingpy_errors'],
                stats['clpa_errors'],
                len(stats['replacements'])),
        '- **Inventory size (avg):** %.2f' % tr.report['stats']['inventory_size'],
    ]
    print('\n'.join(stats_lines))
    lines.extend(stats_lines)

    jsonlib.dump(report_by_cldfds, ds.dir.joinpath('README.json'))
    with ds.dir.joinpath('README.md').open('w', encoding='utf8') as fp:
        fp.write('\n'.join(lines + trlines))
    print(ds.dir.joinpath('README.md'))


def check(args):
    """Checks questionaires for completeness and validity.

    lexibank check [GLOTTOCODE]*

    If no GLOTTOCODEs are specified, all questionaires are checked.
    """
    pass


def main():
    parser = ArgumentParser('pylexibank', readme, download, cldf, ls, report)
    parser.add_argument(
        '--lexibank-repos',
        help="path to lexibank data repository",
        default=Path(pylexibank.__file__).parent.parent)
    parser.add_argument(
        '--glottolog-repos',
        help="path to glottolog data repository",
        default=HOME.joinpath('venvs', 'glottolog3', 'glottolog'))
    parser.add_argument(
        '--concepticon-repos',
        help="path to concepticon data repository",
        default=HOME.joinpath('venvs', 'concepticon', 'concepticon-data'))
    sys.exit(parser.main())
