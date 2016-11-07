# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.dataset import CldfDataset
from clldutils.misc import slug
from clldutils.dsv import UnicodeReader

from pylexibank.lingpy_util import getEvoBibAsSource, iter_alignments
from pylexibank.util import xls2csv 
import lingpy as lp

PROVIDER = 'Deepadung2015'
TRANSCRIPTION_REPORT_CFG = {'column': 'Segments', 'segmentized': True}
CONVERSION = {
    "ә": "ə",
    "ă": "ă",
    "әː": "əː",
    "j̊": "j̊",
    "hh": "h + h",
    "+s": "+ s",
    "ә:": "əː",
    "kk": "kː",
    "nn": "nː",
    "pp": "pː",
    "ᶊ": "ʂ",
    "Ɂ": "ʔ",
    "?": "ʔ"
}
PREPARSE = [(" ", "+")]
CORRECT = {"sәp,": "sәp"}


def download(dataset, **kw):
    xls2csv(dataset.raw.joinpath('100item-phylo.xlsx'))


def cldf(dataset, concepticon, **kw):
    concept_map = {
        c.english: c.concepticon_id for c in dataset.conceptlist.concepts.values()}
    glotto_map = {c['NAME']: c['GLOTTOCODE'] for c in dataset.languages}

    # retrieve coordinates
    coords = {}
    langs = []
    # language map, as the names are not identical
    language_map = {
        "Namhsan": "Nam Hsan",
        "Pangkham": "Pang Kham",
        "Xiang Zhai Tang  (Xiang Cai Tang)": "Xiang Zhai Tang"}
    with UnicodeReader(dataset.raw.joinpath('100item-phylo.Sheet2.csv')) as reader:
        for i, (num, lat, lon, village, country) in enumerate(reader):
            if i >= 1:
                coords[language_map.get(village, village)] = (lat, lon)
                langs.append(language_map.get(village, village))

    cognates = []
    idx = 1
    with UnicodeReader(dataset.raw.joinpath('100item-phylo.Sheet1.csv'),
            delimiter=',') as reader,\
            CldfDataset((
                'ID',
                'Language_ID',
                'Language_name',
                'Language_iso',
                'Parameter_ID',
                'Parameter_name',
                'Value',
                'Source',
                'Segments',
                'Cognacy'
                ), dataset) as ds:
        ds.sources.add(getEvoBibAsSource('Deepadung2015'))
        ds.metadata['coordinates'] = coords
        data = list(reader)
        header = data[2][2:]
        for i, row in enumerate(data[5:]):
            row = [c.strip() for c in row]
            concept = row[1]
            cid = concept_map[concept]
            for j in range(0, len(header), 2):
                lang = language_map.get(header[j], header[j])
                gcid = glotto_map[lang]
                cog = slug(concept)+'-'+row[2:][j+1]
                certainty = 0
                if ' or ' in cog:
                    cog = cog.split(' ')[0]
                    certainty = 1
                word = CORRECT.get(row[2:][j], row[2:][j])
                if word.strip() and ''.join(set(word.strip())) != '-':
                    segments = lp.sequence.sound_classes.clean_string(
                        word,
                        splitters=',',
                        rules=CONVERSION,
                        preparse=PREPARSE,
                        semi_diacritics="")[0]
                    cogid = slug(concept)+'-'+cog
                    ds.add_row([
                        idx, gcid, lang, '', cid, concept, word, PROVIDER, segments,
                        cogid])
                    cognates.append([
                        idx,
                        ds.name,
                        word,
                        cogid,
                        str(certainty),
                        'expert',
                        PROVIDER,
                        '',
                        '',
                        ''])
                    idx += 1
    dataset.cognates.extend(iter_alignments(ds, cognates, method='progressive', ))
