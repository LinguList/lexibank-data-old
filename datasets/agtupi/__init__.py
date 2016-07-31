# coding=utf-8
from __future__ import unicode_literals, print_function
import re
from collections import defaultdict
import unicodedata
from itertools import chain

from pylexibank.dataset import CldfDataset, REQUIRED_FIELDS


def download(dataset, **kw):
    # http://www.scielo.br/pdf/bgoeldi/v10n2/2178-2547-bgoeldi-10-02-00229.pdf
    # pdftotext -raw -nopgbrk  galucio-tupi.pdf galucio-tupi.txt
    raise NotImplemented


def parse(fname, lmap):
    concept_line = re.compile('(?P<ID>[0-9]{3})-(?P<GLOSS>.+)$')
    concept, words, missing, in_appendix = None, '', '', False
    with fname.open(encoding='utf8') as fp:
        pages = fp.read().split('\f')
    for line in chain(*[p.split('\n')[2:] for p in pages]):
        line = line.strip()
        if not line:
            continue

        if line.startswith('APPENDIX 1:'):
            in_appendix = True
            continue

        if line.startswith('APPENDIX 2:'):
            break

        if not in_appendix:
            continue

        match = concept_line.match(line)
        if match:
            if concept:
                yield concept, words, missing
            concept, words, missing = match.group('GLOSS'), '', ''
        else:
            if line.startswith('('):
                assert line.endswith(')') and not missing
                missing = line[1:-1].strip()
            else:
                words += unicodedata.normalize("NFC", line.strip())

    yield concept, words, missing


def parse_cogset(s, lmap):
    def pairs(l):
        for i in range(0, len(l), 2):
            yield l[i:i + 2]

    lid_pattern = re.compile(
        '(?:^|(?:,?\s+|,\s*))(?P<i>%s)\s+' % '|'.join(list(lmap.keys())))
    #s = s.replace(',\u0301', '\u0301,')
    res = defaultdict(list)
    for language, words in pairs(lid_pattern.split(s)[1:]):
        for word in words.split(','):
            word = word.strip()
            if word:
                res[language].append(word)
    return res


def parse_words(s, lmap):
    for cogset in s.split('||'):
        cogset = cogset.strip()
        if cogset:
            if cogset.startswith('(') and cogset.endswith(')'):
                match = re.match(
                    '((?P<lid>%s)\s*\?\s*)+$' % '|'.join(list(lmap.keys())),
                    cogset[1:-1])
                assert match
                yield {lid: [] for lid in cogset[1:-1].replace('?', ' ').split()}
            else:
                yield parse_cogset(cogset, lmap)


LANGUAGE_ID_FIXES = {
    'ALL': ('Tp', 'Ta'),  # set([u'Tp']) set([u'Ta'])
    'PERSON': ('Pa', 'Pt'),  # set([u'Pa']) set([u'Pt'])
    'FISH': ('Pa', 'Pt'),  # set([u'Pa']) set([u'Mw', u'Pt'])
    'TREE': ('Tp', 'Tu'),  # set([u'Tp']) set([u'Mw', u'Tu'])
    'DRINK': ('Tp', 'Ta'),  # set([u'Tp']) set([u'Kt', u'Ta'])
    'SMOKE': ('Tp', 'Ta'),  # set([u'Tp']) set([u'Ta'])
    'GREEN': ('Tg', 'Pg'),  # set([u'Tg']) set([u'Pg'])
    'NAME': ('Tp', 'Ta'),  # set([u'Tp']) set([u'Ta'])
}


def cldf(dataset, glottolog, concepticon, **kw):
    concepticon = {
        c['ENGLISH']: c['CONCEPTICON_ID']
        for c in concepticon.conceptlist(dataset.conceptlist)}
    lmap = {l['ID']: l['GLOTTOCODE'] or None for l in dataset.languages}

    cognate_sets = defaultdict(list)
    for c, w, missing in parse(dataset.raw.joinpath('galucio-tupi.txt'), lmap):
        assert c in concepticon
        if c in LANGUAGE_ID_FIXES:
            f, t = LANGUAGE_ID_FIXES[c]
            w = re.sub(f + '\s+', t + ' ', w, count=1)
            missing = re.sub(f + '\s+', t + ' ', missing, count=1)

        if missing:
            assert re.match(
                '((?P<lid>%s)\s*\?\s*)+$' % '|'.join(list(lmap.keys())), missing)
        missing = missing.replace('?', ' ').split()

        lids = set(missing[:])
        for m in re.finditer('(?P<lid>[A-Z][a-z])\s+', w):
            lids.add(m.group('lid'))
        # make sure all language IDs are valid
        assert not lids.difference(set(lmap.keys()))

        nlids = missing[:]
        for cs in parse_words(w, lmap):
            cognate_sets[c].append(cs)
            nlids.extend(list(cs.keys()))
        nlids = set(nlids)
        assert nlids == lids  # make sure we found all expected language IDs

    with CldfDataset(REQUIRED_FIELDS, dataset) as ds:
        pass
