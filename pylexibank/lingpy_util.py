# coding=utf-8
from __future__ import unicode_literals, print_function
from collections import defaultdict
import zipfile
import json

from clldutils.path import as_posix, copy
from clldutils.misc import slug
from six.moves.urllib.request import urlretrieve, urlopen
from lingpy.sequence.sound_classes import clean_string, tokens2class
import lingpy as lp
import pyclpa
from pybtex import database

from pylexibank.util import with_temp_dir


def getEvoBibAsSource(key):
    """Download bibtex format and parse it from EvoBib"""
    return database.parse_string(
        urlopen("http://bibliography.lingpy.org/raw.php?key="+key).read().decode('utf-8'),
        bib_format='bibtex')


def download_and_unpack_zipfiles(url, dataset, *paths):
    """Download zipfiles and immediately unpack the content"""
    with with_temp_dir() as tmpdir:
        urlretrieve(url, tmpdir.joinpath('ds.zip').as_posix())
        with zipfile.ZipFile(tmpdir.joinpath('ds.zip').as_posix()) as zipf:
            for path in paths:
                zipf.extract(as_posix(path), path=tmpdir.as_posix())
                copy(tmpdir.joinpath(path), dataset.raw)


def test_sequence(sequence, clpa=None, errors=None, stats=None, **keywords):
    """
    Test a sequence for compatibility with CLPA and LingPy.
    """
    clpa = clpa or pyclpa.clpa
    
    # clean the string at first, we only take the first item, ignore the rest
    segments = clean_string(sequence, **keywords)[0].split(' ')
    
    errors = errors or defaultdict(set)
    stats = stats or defaultdict(int)

    # lingpy errors
    lingpy_analysis = [x if y != '0' else '?' for x, y in zip(
        segments, tokens2class(segments, 'dolgo'))]
    clpa_analysis, _sounds, _errors = pyclpa.clpa.check_sequence(segments)

    for a, b, c in zip(segments, lingpy_analysis, clpa_analysis):
        if a[0] in clpa.accents:
            a = a[1:]
        if c[0] in clpa.accents:
            c = c[1:]
        stats[a] += 1
        if b == '?':
            errors[a].add('lingpy')
        if c != a:
            errors[a].add('clpa' if c == '?' else c)

    return segments, [clpa.segment2clpa(x) for x in clpa_analysis], errors, stats


def test_sequences(dataset, column, clpa=False, print_markdown=False, **keywords):
    """
    Write a detailed transcription-report for a CLDF dataset in LexiBank.
    """
    errors = defaultdict(list)
    stats = defaultdict(int)

    # important to make the analysis fast: load clpa only ONCE
    clpa = clpa or pyclpa.clpa
    
    # store also language-specific values
    languages = { tax : dict(stats=defaultdict(int),
        errors=defaultdict(list)) for tax in set(
            [row['Language_name'] for row in dataset.rows]
            )}
    for row in dataset.rows:
        segs, ids, _errors, _stats = test_sequence(
            row[column], errors=defaultdict(list), stats=defaultdict(int), **keywords)
        for itm, val in _errors.items(): 
            errors[itm] += val
            languages[row['Language_name']]['errors'][itm] += val
        for itm, val in _stats.items(): 
            stats[itm] += val
            languages[row['Language_name']]['stats'][itm] += val

    # write report
    number_of_tokens = sum(stats.values())
    number_of_segments = len(stats)
    number_of_errors = len(errors)
    number_of_lingpy_errors = sum([1 if 'lingpy' in errors[x] else 0 for x in errors])
    number_of_clpa_errors = sum([1 if 'clpa' in errors[x] else 0 for x in errors])
    inventory_size = sum([len(language['stats']) for language in
        languages.values()]) / len(languages)
    modified = []
    for error, values in errors.items():
        newvals = [v for v in values if v not in ['lingpy', 'clpa']]
        if newvals:
            modified += [(error, ', '.join(newvals))]

    # correct for problematic clpa-structure (should be changed in clpa) xxx
    for language in languages:
        for itm, val in languages[language]['errors'].items():
            languages[language]['errors'] = dict([(v, val.count(v)) for v in
                set(val)])
    for itm, val in errors.items():
        errors[itm] = dict([(v, val.count(v)) for v in set(val)])

    # json-form for transcription report for the dataset
    rpt = dict(
            number_of_tokens = number_of_tokens,
            number_of_segments = number_of_segments,
            number_of_errors = dict(
                lingpy = number_of_lingpy_errors,
                clpa = number_of_clpa_errors
                ),
            inventory_size = inventory_size,
            modified_for_clpa = dict(modified),
            segments = stats,
            errors = errors,
            varieties = languages
            )
    dataset.metadata['transcription'] = rpt
        
    text = """# Transcription Report for {dataset}
## General Statistics
* Number of Tokens: {NOT}
* Number of Segments: {NOS}
* Number of Errors: {NOE}
* Number of LingPy-Errors: {NOL}
* Number of CLPA-Errors: {NOC}
* Inventory Size: {IVS:.2f}
{modified}
## Detailed listing of recognized segments
{segments}
"""
    segments = '| Segment | Occurrence | LingPy | CLPA | \n|---|---|---|---|\n'
    for a, b in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        if a in errors:
            c = '✓' if 'lingpy' not in errors[a] else '?'
            d = ', '.join(errors[a]) if 'clpa' not in errors[a] else '?'
        else:
            c, d = '✓', '✓'
        segments += '| {0} | {1} | {2} | {3} |\n'.format(a, b, c, d)
    
    if print_markdown:
        print(text.format(
            dataset=dataset.name,
            NOT=number_of_tokens,
            NOS=number_of_segments,
            NOE=number_of_errors,
            NOL=number_of_lingpy_errors,
            NOC=number_of_clpa_errors,
            IVS=inventory_size,
            modified='\n## Automatically modified (CLPA)\n' +
            '| Source | Target |\n|---|---|\n' +
            ''.join(['| {0} | {1} |\n'.format(a, b) for a, b in modified])
            if modified else '',
            segments=segments))

def _cldf2wld(dataset):
    """Make lingpy-compatible dictinary out of cldf main data."""
    header = [h for h in dataset.rows[0].keys() if h != 'ID']
    D = {0: ['lid'] + [h.lower() for h in header]}
    for idx, row in enumerate(dataset.rows):
        D[idx + 1] = ['lid'] + [row[h] for h in header]
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


def automatic_cognates(
        dataset, column='Segments', method='turchin', threshold=0.5, **keywords):
    """
    Compute cognates automatically for a given dataset.
    """
    if method == 'turchin':
        cognates = []
        for row in dataset.rows:
            sounds = ''.join(tokens2class(row[column].split(' '), 'dolgo'))
            if sounds.startswith('V'):
                sounds = 'H' + sounds
            sounds = '-'.join([s for s in sounds if s != 'V'][:2])
            cogid = slug(row['Parameter_name'])+'-'+sounds
            if not '0' in sounds:
                cognates += [(row['ID'], dataset.name, row['Value'], cogid, 'turchin')]
        return cognates
    
    if method in ['sca', 'lexstat']:
        lex = _cldf2lexstat(dataset)
        if method == 'lexstat':
            lex.get_scorer(**keywords)
        lex.cluster(method=method, threshold=threshold, ref='cogid')
        cognates = []
        for k in lex:
            cognates += [(lex[k, 'lid'], dataset.name, lex[k, 'value'], lex[k,
                'cogid'], method+'-t{0:.2f}'.format(threshold))]
        return cognates


def automatic_alignments(dataset, cognate_sets, column='Segments', method='library'):
    """
    Function computes automatic alignments and writes them to file.
    """
    wordlist = _cldf2wordlist(dataset)
    cognates = {}
    for row in cognate_sets:
        lid = row[0]
        cogid = row[-2]
        cognates[lid] = cogid
    wordlist.add_entries('cogid', 'lid', lambda x: cognates[x] if x in cognates
            else '')
    idx = 1
    for k in wordlist:
        if not wordlist[k, 'cogid']:
            wordlist[k][wordlist.header['cogid']] = 'empty-'+str(idx)
            idx += 1

    alm = lp.Alignments(
        wordlist,
        ref='cogid',
        row='parameter_name',
        col='language_name',
        segments=column.lower())
    alm.align(method=method)
    alignments = []
    for k in alm:
        alignments += [(alm[k, 'lid'], dataset.name, alm[k, 'alignment'], alm[k, 'cogid'], method)]
    return alignments
