# coding=utf-8
from __future__ import unicode_literals, print_function
import re
import unicodedata

from pylexibank.dataset import CldfDataset, REQUIRED_FIELDS


def download(dataset, **kw):
    raise NotImplemented


def parse_txt(fname):
    concept_line = re.compile('(?P<ID>[0-9]{3})-(?P<GLOSS>.+)$')
    concept, words = None, ''
    for line in fname.open(encoding='utf8'):
        match = concept_line.match(line)
        if match:
            if concept:
                yield concept, words
            concept = match.group('GLOSS')
            words = ''
        elif line.strip():
            words += ' ' + unicodedata.normalize("NFC", line.strip())
    yield concept, words


def parse_cogset(s, lmap):
    yield s


def parse_words(s, lmap):
    for cogset in s.split('||'):
        cogset = cogset.strip()
        if cogset:
            if cogset.startswith('(') and cogset.endswith(')'):
                try:
                    assert re.match(
                        '((?P<lid>%s)\s+\?\s*)+$' % '|'.join(list(lmap.keys())),
                        cogset[1:-1])
                except:
                    print(s)
                    raise
            yield parse_cogset(cogset, lmap)


def cldf(dataset, glottolog, concepticon, **kw):
    concepticon = {
        c['ENGLISH']: c['CONCEPTICON_ID']
        for c in concepticon.conceptlist(dataset.conceptlist)}
    language_map = {l['ID']: l['GLOTTOCODE'] or None for l in dataset.languages}

    print('|'.join(sorted(list(language_map.keys()))))
    return
    for c, w in parse_txt(dataset.raw.joinpath('swadesh.txt')):
        assert c in concepticon
        list(parse_words(w, language_map))

    with CldfDataset(REQUIRED_FIELDS, dataset) as ds:
        pass
