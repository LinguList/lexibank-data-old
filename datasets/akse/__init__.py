# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.dsv import UnicodeReader
from clldutils.misc import slug

from pylexibank.util import xls2csv
from pylexibank.dataset import CldfDataset, valid_Value as vv_base


def download(dataset):
    xls2csv(dataset.raw.joinpath('Semitic.Wordlists.xls'), outdir=dataset.raw)


def valid_Value(row):
    return vv_base(row) and row['Value'] != '---'


def cldf(dataset, glottolog, concepticon, **kw):
    concepticon = {
        c['ENGLISH']: c['CONCEPTICON_ID']
        for c in concepticon.conceptlist(dataset.conceptlist)}

    language_map = {l['NAME']: l['GLOTTOCODE'] or None for l in dataset.languages}

    header, rows = None, []
    with UnicodeReader(
            dataset.raw.joinpath('Semitic.Wordlists.ActualWordlists.csv')) as reader:
        for i, row in enumerate(reader):
            row = [c.strip() for c in row]
            if i == 0:
                header = row
            if i > 0:
                rows.append(row)

    langs = header[1:]
    with CldfDataset((
            'ID',
            'Language_ID',
            'Language_name',
            'Parameter_ID',
            'Parameter_name',
            'Value',
            ),
            dataset) as ds:
        for row in rows:
            concept = row[0]
            for i, col in enumerate(row[1:]):
                lang = langs[i]
                ds.add_row([
                    '%s-%s' % (slug(lang), slug(concept)),
                    language_map[lang],
                    lang,
                    concepticon[concept],
                    concept,
                    col,
                ])
