"""
Main command line interface of the pylexibank package.

Like programs such as git, this cli splits its functionality into sub-commands
(see e.g. https://docs.python.org/2/library/argparse.html#sub-commands).
The rationale behind this is that while a lot of different tasks may be
triggered using this cli, most of them require common configuration.

The basic invocation looks like

    lexibank [OPTIONS] <command> [args]

"""
from __future__ import unicode_literals
import os
import sys
from time import time

from clldutils.clilib import ArgumentParser, ParserError
from clldutils.path import Path

import pylexibank
from pylexibank.util import data_path, formatted_number
from pylexibank.dataset import Dataset, synonymy_index


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


def report(args):
    """
    """
    get_dataset(args).report()


def list_(args):
    for d in data_path(repos=Path(args.lexibank_repos)).iterdir():
        if is_dataset_dir(d):
            ds = Dataset(d)
            print(d.name, ds.md['dc:title'])


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
                func(get_dataset(args, d.name), **vars(args))
                print('... done %s [%.1f secs]' % (d.name, time() - s))


def cldf(args):
    """
    Create CLDF datasets from the raw data for a dataset.

    lexibank cldf [DATASET_ID]
    """
    def _cldf(ds, **kw):
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
    if not list(ds.cldf_dir.glob('*.csv')):
        return
    lines = [
        '## %s' % ds.md.get('dc:title'),
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

    lines.extend([
        '### Cognate sets',
        '%s cognates in %s cognate sets' % tuple(
            map(formatted_number, ds.cognate_stats())),
        '',
        '### Lexemes',
        '',
        ' | '.join(['Name', 'Languages', 'Concepts', 'Lexemes', 'Synonymy', 'Quality']),
        '|'.join([':--- ', ' ---:', ' ---:', ' ---:', ' ---:', ':---:']),
    ])

    totals = ['**total:**', set(), set(), 0, (0, 0), '']

    dslines = []
    trlines = []
    trtotals = []
    for cldfds in sorted(ds.iter_cldf_datasets(), key=lambda m: m.name):
        badges = [
            get_badge(cldfds.rows, 'Glottolog', 'Language_ID'),
            get_badge(cldfds.rows, 'Concepticon', 'Parameter_ID'),
            get_badge(cldfds.rows, 'Source'),
        ]
        if 'transcription' in cldfds.metadata:
            new_badges, new_lines = _transcription_readme(
                    cldfds.metadata['transcription'])
            new_badges
            trlines.append(
                    '[%s](%s)' % (cldfds.name, 'cldf/%s.csv' % cldfds.name) \
                            + ' | {0} | {1} | {2} | {3} | {4:.2f} | '.format(
                                *new_lines) + \
                                        ' '.join(new_badges)
                            )
            trtotals.append(new_lines)

        stats = cldfds.stats
        params = len(stats['parameters'])
        sindex, langs = synonymy_index(cldfds)
        if langs:
            sindex /= float(len(langs))
        else:
            sindex = 0
        totals[1] = totals[1].union(langs)
        totals[2] = totals[2].union(stats['parameters'])
        totals[3] += len(cldfds)
        totals[4] = (totals[4][0] + sindex, totals[4][1] + 1)

        dslines.append(' | '.join([
            '[%s](%s)' % (cldfds.name, 'cldf/%s.csv' % cldfds.name),
            '%s' % len(langs),
            '%s' % params,
            '%s' % len(cldfds),
            '%.2f' % sindex,
            ' '.join(badges)]))

    if trlines:
        trtotals = [sum([line[i] for line in trtotals]) for i in
                range(len(trtotals[0]))]
        trtotals[-1] = trtotals[-1] / len(trlines)
        trlines = [
                '', 
                '### Sounds', 
                '',
                'Name  | Sounds (total) | Sounds (unique) | '+\
                        'Errors (LingPy) | Errors (CLPA) | '+\
                        'Inventory (mean) | Quality ',
                        ':---| ---: | ---:| ---:| ---:| ---:| :---:|',
                        '**total** | {0} | {1} | {2} | {3} | {4:.2f} | '.format(
                            *trtotals)
                        ]+\
                        trlines

    for i in range(1, 4):
        totals[i] = formatted_number(totals[i])
    totals[4] = '%.2f' % (totals[4][0] / totals[4][1])

    with ds.dir.joinpath('README.md').open('w', encoding='utf8') as fp:
        fp.write('\n'.join(lines + [' | '.join(totals)] + dslines + trlines))
    print(ds.dir.joinpath('README.md'))

def _transcription_readme(transcription):

    # extend by transcription
    lines = [
            transcription['number_of_tokens'],
            transcription['number_of_segments'],
            transcription['number_of_errors']['lingpy'],
            transcription['number_of_errors']['clpa'],
            transcription['inventory_size']
        ]
    
    badges = [get_badge(
            None, 'LingPy', 
            ratio=(transcription['number_of_segments']-\
                    transcription['number_of_errors']['lingpy'])/\
                    transcription['number_of_segments']
        ),
        get_badge(
            None, 'CLPA', 
            ratio=(transcription['number_of_segments']-\
                    transcription['number_of_errors']['clpa'])/\
                    transcription['number_of_segments']
        )]
    return badges, lines


def check(args):
    """Checks questionaires for completeness and validity.

    lexibank check [GLOTTOCODE]*

    If no GLOTTOCODEs are specified, all questionaires are checked.
    """
    pass


def main():
    parser = ArgumentParser('pylexibank', readme, download, cldf, list_, report)
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
