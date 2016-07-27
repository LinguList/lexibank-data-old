# coding=utf-8
from __future__ import unicode_literals, print_function
from collections import defaultdict
import zipfile

from clldutils.path import as_posix, copy
from six.moves.urllib.request import urlretrieve, urlopen
from lingpy.sequence.sound_classes import clean_string, tokens2class
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


def test_sequences(dataset, column, clpa=False, **keywords):
    errors = defaultdict(list)
    stats = defaultdict(int)

    # important to make the analysis fast: load clpa only ONCE
    clpa = clpa or pyclpa.clpa
    
    for row in dataset.rows:
        segs, ids, errors, stats = test_sequence(
            row[column], errors=errors, stats=stats, **keywords)

    # write report
    number_of_tokens = sum(stats.values())
    number_of_segments = len(stats)
    number_of_errors = len(errors)
    number_of_lingpy_errors = sum([1 if 'lingpy' in errors[x] else 0 for x in errors])
    number_of_clpa_errors = sum([1 if 'clpa' in errors[x] else 0 for x in errors])
    modified = []
    for error, values in errors.items():
        newvals = [v for v in values if v not in ['lingpy', 'clpa']]
        if newvals:
            modified += [(error, ', '.join(newvals))]
        
    text = """# Transcription Report for {dataset}
## General Statistics
* Number of Tokens: {NOT}
* Number of Segments: {NOS}
* Number of Errors: {NOE}
* Number of LingPy-Errors: {NOL}
* Number of CLPA-Errors: {NOC}
{modified}
## Detailed listing of recognized segments
{segments}
"""
    segments = '| Segment | Occurrence | LingPy | CLPA | \n |---|---|---|---|\n'
    for a, b in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        if a in errors:
            c = '✓' if 'lingpy' not in errors[a] else '?'
            d = ', '.join(errors[a]) if 'clpa' not in errors[a] else '?'
        else:
            c, d = '✓', '✓'
        segments += '| {0} | {1} | {2} | {3} |\n'.format(a, b, c, d)

    print(text.format(
        dataset=dataset.name,
        NOT=number_of_tokens,
        NOS=number_of_segments,
        NOE=number_of_errors,
        NOL=number_of_lingpy_errors,
        NOC=number_of_clpa_errors,
        modified='\n## Automatically modified (CLPA)\n' +
        '| Source | Target |\n|---|---|\n' +
        ''.join(['| {0} | {1} |\n'.format(a, b) for a, b in modified])
        if modified else '',
        segments=segments))

