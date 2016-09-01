# coding: utf8
from __future__ import unicode_literals, print_function, division
from itertools import izip_longest
from collections import OrderedDict, defaultdict

from clldutils.dsv import UnicodeReader
from clldutils.misc import slug
from pycldf.sources import Source

from pylexibank.util import xls2csv
from pylexibank.dataset import CldfDataset, Unmapped
from pylexibank.lingpy_util import (clean_string, iter_alignments,
        wordlist2cognates, getEvoBibAsSource)
import lingpy as lp


PROVIDER = "Lees2013"
SOURCE = "Hattori1960"


def download(dataset):
    xls2csv(dataset.raw.joinpath('AinuHattoriChiri.xlsx'), outdir=dataset.raw)


class Wordlist(object):
    def __init__(self, language):
        self.language = language
        self.words = OrderedDict()


def read_csv(dataset):
    header = None
    with UnicodeReader(dataset.raw.joinpath('AinuHattoriChiri.Sheet1.csv')) as reader:
        for i, row in enumerate(reader):
            row = [c.strip() for c in row]
            if i == 1:
                header = row[2:]
            if i > 2:
                wl = Wordlist(row[1])
                words, concept = None, None
                for j in range(len(header)):
                    if header[j]:
                        # a column containing words
                        if words:
                            assert concept
                            wl.words[concept] = (words, [])
                            words, concept = None, None
                        words = row[j + 2].split(';')
                        concept = header[j]
                    else:
                        # a column containing cognate set IDs
                        assert concept
                        words = [w for w in words if w != '#']
                        if words:
                            wl.words[concept] = (
                                words,
                                [int(float(k)) for k in row[j + 2].split('&') if k != '#']
                            )
                        words, concept = None, None
                yield wl


def cldf(dataset, glottolog, concepticon, **kw):
    language_map = {l['NAME']: l['GLOTTOCODE'] or None for l in dataset.languages}
    concept_map = {c['ENGLISH']: c['CONCEPTICON_ID']
                   for c in concepticon.conceptlist(dataset.conceptlist)}
    wordlists = list(read_csv(dataset))
    cogsets = defaultdict(lambda: defaultdict(list))
    for wl in wordlists:
        for concept, (words, cogids) in wl.words.items():
            if len(cogids) == 1:
                cogsets[concept][cogids[0]].append(words[0])

    with CldfDataset((
        'ID',
        'Language_ID',
        'Language_name',
        'Parameter_ID',
        'Parameter_name',
        'Value',
        'Source',
        'Comment',
    ), dataset) as ds:
        for wl in wordlists:
            #print(wl.language)
            for concept, (words, cogids) in wl.words.items():
                if len(cogids) > 1:
                    if len(words) < len(cogids):
                        if len(words) == 1:
                            if ':' in words[0]:
                                words = words[0].split(':')
                            if ',' in words[0]:
                                words = words[0].split(',')
                        assert len(words) >= len(cogids)
                    print('    # Language {0} concept {1}'.format(wl.language, concept))
                    for cogid in cogids:
                        print('    # {0}: {1}'.format(cogid, '; '.join(cogsets[concept][cogid])))
                    print('    {')
                    for word, cogid in izip_longest(words, cogids):
                        print('        "%s": %s,' % (word, cogid))
                    print('    },')
                    #print('    (%s, %s),' % (words, cogids))
                pass
