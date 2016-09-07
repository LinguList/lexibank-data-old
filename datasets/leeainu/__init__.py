# coding: utf8
from __future__ import unicode_literals, print_function, division
from six.moves import zip_longest as izip_longest
from collections import OrderedDict, defaultdict

from clldutils.dsv import UnicodeReader
from clldutils.misc import slug

from pylexibank.util import xls2csv
from pylexibank.dataset import CldfDataset
from pylexibank.lingpy_util import (clean_string, iter_alignments,
        wordlist2cognates, getEvoBibAsSource)
import lingpy as lp

from .cogsets import COGSET_MAP

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
                        words = [w for w in words if w and w != '#']
                        if words:
                            wl.words[concept] = (
                                words,
                                [int(float(k)) for k in row[j + 2].split('&') if k != '#']
                            )
                        words, concept = None, None
                yield wl


def cldf(dataset, concepticon, **kw):
    language_map = {l['NAME']: l['GLOTTOCODE'] or None for l in dataset.languages}
    concept_map = {c['ENGLISH']: c['CONCEPTICON_ID']
                   for c in concepticon.conceptlist(dataset.conceptlist)}
    concept_map['year'] = '1226' # dunno why this is missing, it's 200 words...
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
        'Segments',
        'Source',
        'Comment',
    ), dataset) as ds:
        ds.sources.add(getEvoBibAsSource(SOURCE))
        cognates = []
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
                    assert (wl.language, concept) in COGSET_MAP
                    if len(words) > len(cogids):
                        assert (wl.language, concept) in COGSET_MAP
                if (wl.language, concept) in COGSET_MAP:
                    word_to_cogid = COGSET_MAP[(wl.language, concept)]
                else:
                    word_to_cogid = dict(izip_longest(words, cogids))
                for i, word in enumerate(words):
                    if word.startswith('(') and word.endswith(')'):
                        word = word[1:-1].strip()
                    wid = '%s-%s-%s' % (slug(wl.language), slug(concept), i + 1)
                    ds.add_row([
                        wid,
                        '',
                        wl.language,
                        concept_map.get(concept, ''),
                        concept,
                        word,
                        clean_string(word, splitters='?')[0],
                        SOURCE,
                        '',
                    ])
                    if word_to_cogid.get(word):
                        cognates.append([
                            wid,
                            ds.name,
                            word,
                            '%s-%s' % (slug(concept), word_to_cogid[word]),
                            False,
                            'expert',
                            SOURCE,
                            '',
                            '',
                            '',
                        ])
        dataset.cognates.extend(iter_alignments(ds, cognates, column='Segments'))
