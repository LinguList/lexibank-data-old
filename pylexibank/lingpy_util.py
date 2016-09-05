# coding=utf-8
from __future__ import unicode_literals, print_function
from collections import defaultdict, Counter

from clldutils.misc import slug
from six.moves.urllib.request import urlopen
from lingpy.sequence.sound_classes import clean_string, tokens2class
import lingpy as lp
from pyclpa.base import get_clpa
from pybtex import database


clpa = get_clpa()


def getEvoBibAsSource(key):
    """Download bibtex format and parse it from EvoBib"""
    return database.parse_string(
        urlopen("http://bibliography.lingpy.org/raw.php?key="+key).read().decode('utf-8'),
        bib_format='bibtex')


def wordlist2cognates(wordlist, dataset, source, expert='expert', ref='cogid'):
    """Turn a wordlist into a cognate set list, using the cldf parameters."""
    return [[
        wordlist[k, 'lid'],
        dataset.name, 
        wordlist[k, 'ipa'],
        '{0}-{1}'.format(slug(wordlist[k, 'concept']), wordlist[k, ref]),
        '',
        expert,
        source,
        '', '', ''] for k in wordlist]


def getSourceFromBibTex(source):
    "utility function to read source from bibtex"
    return database.parse_string(source, bib_format="bibtex")


def test_sequence(sequence, **keywords):
    """
    Test a sequence for compatibility with CLPA and LingPy.
    """
    invalid = Counter()
    segment_count = Counter()
    lingpy_errors = set()
    clpa_errors = set()
    clpa_repl = defaultdict(set)

    # clean the string at first, we only take the first item, ignore the rest
    try:
        segments = clean_string(sequence, **keywords)[0].split(' ')
        lingpy_analysis = [
            x if y != '0' else '?' for x, y in
            zip(segments, tokens2class(segments, 'dolgo'))]
        clpa_analysis, _sounds, _errors = clpa.check_sequence(segments)
        general_errors = len(['?' for x in zip(
            lingpy_analysis,
            clpa_analysis) if '?' in x])
    except (ValueError, IndexError):
        invalid.update([sequence])
        segments, clpa_analysis = [], []

    if segments:
        for a, b, c in zip(segments, lingpy_analysis, clpa_analysis):
            if a[0] in clpa.accents:
                a = a[1:]
            if c[0] in clpa.accents:
                c = c[1:]
            segment_count.update([a])
            if b == '?':
                lingpy_errors.add(a)
            if c != a:
                if c == '?':
                    clpa_errors.add(a)
                else:
                    clpa_repl[a].add(c)

    return (
        segments,
        [clpa.segment2clpa(x) for x in clpa_analysis],
        invalid,
        segment_count,
        lingpy_errors,
        clpa_errors,
        clpa_repl,
        general_errors)


def segmentize(dataset, source='Value', target='Segments', clean=lambda s: s, **kw):
    """
    Write a detailed transcription-report for a CLDF dataset in LexiBank.
    """
    for row in dataset.rows:
        res = test_sequence(clean(row[source]), segmentized=False, **kw)
        row[target] = ' '.join(res[0])


def test_sequences(dataset, lid_getter, report, column='Value', **kw):
    """
    Write a detailed transcription-report for a CLDF dataset in LexiBank.
    """
    for row in dataset.rows:
        res = test_sequence(row[column], **kw)
        if not kw['segmentized'] and column != 'Segments' and 'Segments' in row:
            row['Segments'] = ' '.join(res[0])
        lr = report[lid_getter(row)]
        for i, attr in enumerate(['invalid', 'segments', 'lingpy_errors',
            'clpa_errors']):
            lr[attr].update(res[i + 2])
        for segment, repls in res[-2].items():
            lr['replacements'][segment].update(repls)
        lr['general_errors'] += res[-1]
        lr['word_errors'] += 1 if res[-1] else 0
        if res[-1]:
            lr['bad_words'] += [row['ID']]

def _cldf2wld(dataset):
    """Make lingpy-compatible dictinary out of cldf main data."""
    header = [h for h in dataset.rows[0].keys() if h != 'ID']
    D = {0: ['lid'] + [h.lower() for h in header]}
    for idx, row in enumerate(dataset.rows):
        D[idx + 1] = [row['ID']] + [row[h] for h in header]
    return D


def _cldf2lexstat(
        dataset,
        segments='segments',
        transcription='value',
        row='parameter_name',
        col='language_name'):
    """Read LexStat object from cldf dataset."""
    D = _cldf2wld(dataset)
    return lp.LexStat(D, segments=segments, transcription=transcription, row=row, col=col)


def _cldf2wordlist(dataset, row='parameter_name', col='language_name'):
    """Read worldist object from cldf dataset."""
    return lp.Wordlist(_cldf2wld(dataset), row=row, col=col)


def iter_cognates(
        dataset, column='Segments', method='turchin', threshold=0.5, **keywords):
    """
    Compute cognates automatically for a given dataset.
    """
    if method == 'turchin':
        for row in dataset.rows:
            sounds = ''.join(tokens2class(row[column].split(' '), 'dolgo'))
            if sounds.startswith('V'):
                sounds = 'H' + sounds
            sounds = '-'.join([s for s in sounds if s != 'V'][:2])
            cogid = slug(row['Parameter_name'])+'-'+sounds
            if '0' not in sounds:
                yield (
                    row['ID'],
                    dataset.name,
                    row['Value'],
                    cogid,
                    '',
                    'CMM',
                    '',  # cognate source
                    '',  # alignment
                    '',  # alignment method
                    '',  # alignment source
                )

    if method in ['sca', 'lexstat']:
        lex = _cldf2lexstat(dataset)
        if method == 'lexstat':
            lex.get_scorer(**keywords)
        lex.cluster(method=method, threshold=threshold, ref='cogid')
        for k in lex:
            yield (
                lex[k, 'lid'],
                dataset.name,
                lex[k, 'value'],
                lex[k, 'cogid'],
                '',
                method + '-t{0:.2f}'.format(threshold),
                '',  # cognate source
                '',  # alignment
                '',  # alignment method
                '',  # alignment source
            )


def iter_alignments(
        dataset, cognate_sets, column='Segments', method='library', prefix=''):
    """
    Function computes automatic alignments and writes them to file.
    """
    if not isinstance(dataset, lp.basic.parser.QLCParser):
        wordlist = _cldf2wordlist(dataset)
        cognates = {r[0]: r for r in cognate_sets}
        wordlist.add_entries(
            'cogid', 'lid', lambda x: cognates[x][3] if x in cognates else '')
        for i, k in enumerate(wordlist):
            if not wordlist[k, 'cogid']:
                wordlist[k][wordlist.header['cogid']] = 'empty-%s' % i
        alm = lp.Alignments(
            wordlist,
            ref='cogid',
            row='parameter_name',
            col='language_name',
            segments=column.lower())
        alm.align(method=method)
        for k in alm:
            if alm[k, 'lid'] in cognates:
                row = list(cognates[alm[k, 'lid']])
                row[7] = alm[k, 'alignment']
                row[8] = method
                yield row
    else:
        alm = lp.Alignments(dataset, ref='cogid')
        alm.align(method=method)
        for row in cognate_sets:
            try:
                idx = int(row[0].split('-')[1])
            except:
                print(row)
                raise
            row[7] = alm[idx, 'alignment']
            row[8] = 'SCA-'+method
            yield row
