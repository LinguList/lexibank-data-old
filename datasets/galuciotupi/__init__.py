# coding=utf-8
from __future__ import unicode_literals, print_function
import re
from collections import defaultdict
import unicodedata
from itertools import chain

from pylexibank.dataset import CldfDataset
from pylexibank.lingpy_util import segmentize, iter_alignments


def download(dataset, **kw):
    # http://www.scielo.br/pdf/bgoeldi/v10n2/2178-2547-bgoeldi-10-02-00229.pdf
    # pdftotext -raw galucio-tupi.pdf galucio-tupi.txt
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

        # Don't start parsing before entering Appendix 1:
        if line.startswith('APPENDIX 1:'):
            in_appendix = True
            continue

        # Quit parsing once we hit Appendix 2:
        if line.startswith('APPENDIX 2:'):
            break

        if not in_appendix:
            continue

        match = concept_line.match(line)
        if match:
            if concept:
                yield concept, words, missing
            concept, words, missing = (match.group('ID'), match.group('GLOSS')), '', ''
        else:
            if line.startswith('('):
                assert line.endswith(')') and not missing
                missing = line[1:-1].strip()
            else:
                words += unicodedata.normalize("NFC", line.strip())

    yield concept, words, missing


def iter_lang(s, lmap):
    def pairs(l):
        for i in range(0, len(l), 2):
            yield l[i:i + 2]

    lid_pattern = re.compile(
        '(?:^|(?:,?\s+|,\s*))(?P<i>%s)\s+' % '|'.join(list(lmap.keys())))
    for language, words in pairs(lid_pattern.split(s)[1:]):
        yield language, [w.strip() for w in words.split(',') if w.strip()]


def iter_cogsets(s, lmap):
    for cogset in s.split('||'):
        cogset = cogset.strip()
        if cogset:
            yield dict(iter_lang(cogset, lmap))


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


def cldf(dataset, concepticon, **kw):
    concepticon = {
        x.english: x.concepticon_id for x in
        dataset.conceptlist.concepts.values()}
    lmap = {l['ID']: l['GLOTTOCODE'] or None for l in dataset.languages}
    lmap_name = {l['ID']: l['NAME'] or None for l in dataset.languages}

    cognate_sets = defaultdict(list)
    for (cid, c), w, missing in parse(dataset.raw.joinpath('galucio-tupi.txt'), lmap):
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
        for cs in iter_cogsets(w, lmap):
            cognate_sets[(cid, c)].append(cs)
            nlids.extend(list(cs.keys()))
        nlids = set(nlids)
        assert nlids == lids  # make sure we found all expected language IDs

    cognatesets = []
    with CldfDataset(
            ('ID',
             'Language_ID',
             'Language_name',
             'Language_local_ID',
             'Parameter_ID',
             'Parameter_name',
             'Parameter_local_ID',
             'Value',
             'Segments'),
            dataset) as ds:
        for (cid, concept), cogsets in cognate_sets.items():
            for j, cogset in enumerate(cogsets):
                for lid, words in sorted(cogset.items(), key=lambda k: k[0]):
                    for i, word in enumerate(words):
                        wid = '%s-%s-%s-%s' % (lid, cid, j + 1, i + 1)
                        ds.add_row([
                            wid,
                            lmap[lid],
                            lmap_name[lid],
                            lid,
                            concepticon[concept],
                            concept,
                            cid,
                            word,
                            '',
                        ])
                        cognatesets.append([
                            wid,
                            ds.name,
                            word,
                            '%s-%s' % (cid, j + 1),
                            False,
                            'expert',
                            '',
                            '',
                            '',
                            '',
                        ])
        segmentize(ds, clean=lambda s: s.split(' ~ ')[0])
    dataset.cognates.extend(iter_alignments(ds, cognatesets, column='Segments'))
