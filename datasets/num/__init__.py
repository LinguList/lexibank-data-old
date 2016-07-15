# coding=utf-8
from __future__ import unicode_literals, print_function
from itertools import groupby
import re

from pycldf.sources import Source
from clldutils.dsv import UnicodeReader

from pylexibank.util import xls2csv
from pylexibank.dataset import CldfDataset, Unmapped


def download(dataset):
    xls2csv(dataset.raw.joinpath('numeral_010316.xlsx'), outdir=dataset.raw)

"""
numeral_010316.SYSTEM.csv
-------------------------
LG_LINK,NUM_SYSTEM,EDITOR_COMMENT
Aari.htm,20.0,
Abai-Sungai.htm,,

numeral_010316.META.csv
-----------------------
NAME,COUNTRY,ISO,GLOTTO_NAME,GLOTTO_CODE,LG_LINK,AUDIO,SOURCE,NR_SETS,VARIANT
A'tong,"India, Bangladesh",aot,A'tong,aton1241,Atong.htm,,"Dr. ...",2.0,1.0
A'tong,"India, Bangladesh",aot,A'tong,aton1241,Atong.htm,,"Dr. ...",2.0,2.0

numeral_010316.NUMERAL.csv
--------------------------
NUMERAL,TRANS,LG_LINK,VAR,COMMENT,
1.0,wólːáq,Aari.htm,1.0,,
2.0,qastːén,Aari.htm,1.0,,
"""


def read_csv(dataset, what):
    with UnicodeReader(dataset.raw.joinpath('numeral_010316.{0}.csv'.format(what))) as r:
        for i, row in enumerate(r):
            if i:
                yield row


def lgid(n):
    return n.split('.')[0].lower().replace(' ', '_')


def cldf(dataset, glottolog, concepticon, **kw):
    concept_map = {int(c['GLOSS']): c['CONCEPTICON_ID'] or None for c in dataset.concepts}

    gc_pattern = re.compile('[a-z0-9]{4}[1-9][0-9]{3}$')
    meta = {}
    for row in read_csv(dataset, 'META'):
        meta[(row[5], row[9])] = dict(zip(
            'NAME,COUNTRY,ISO,GLOTTO_NAME,GLOTTO_CODE,LG_LINK,AUDIO,SOURCE,NR_SETS,VARIANT'.lower().split(','),
            row))

    sources = {}
    sid = 0
    for spec in meta.values():
        if spec['source'] and spec['source'] not in sources:
            sid += 1
            sources[spec['source']] = Source('misc', 's%s' % sid, title=spec['source'])

    unmapped = Unmapped()
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
        for key, items in groupby(
                sorted(read_csv(dataset, 'NUMERAL'), key=lambda r: (r[2], r[3], r[0])),
                lambda r: (r[2], r[3])):
            if key not in meta:
                continue
            if int(float(key[1])) > 1:
                continue
            md = meta[key]
            source, ref = sources.get(md['source']), None
            if source:
                ds.sources.add(source)
                ref = source.id
            if gc_pattern.match(md['glotto_code']):
                for concept, rows in groupby(items, lambda k: k[0]):
                    if not concept.endswith('.0'):
                        continue
                    iconcept = int(float(concept))
                    if iconcept not in concept_map:
                        unmapped.concepts.add((iconcept,iconcept))
                    for k, row in enumerate(rows):
                        ds.add_row([
                            '%s-%s-%s' % (lgid(row[2]), iconcept, k + 1),
                            md['glotto_code'],
                            md['name'],
                            concept_map.get(iconcept),
                            '%s' % iconcept,
                            row[1],
                            ref,
                            row[4] or None,
                        ])
    unmapped.pprint()