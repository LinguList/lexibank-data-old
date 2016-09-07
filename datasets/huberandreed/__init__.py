# coding=utf-8
from __future__ import unicode_literals, print_function
from itertools import groupby

import lingpy as lp
from clldutils.misc import slug

from pylexibank.dataset import CldfDataset
from pylexibank.providers import qlc
from pylexibank.lingpy_util import getSourceFromBibTex

SOURCE = """@book{Huber1992,author={Huber, Randall Q. and Reed, Robert B.},
title={Comparative vocabulary. Selected words in indigenous languages of
Columbia.}, address={Santafé de Bogotá}, publisher={Instituto lingüístico de
Veterano}}"""

FNAME = 'huber1992.csv'


def download(dataset, **kw):
    qlc.download(dataset, FNAME)


def cldf(dataset, concepticon, **kw):
    # column "counterpart_doculect" gives us the proper names of the doculects
    wl = lp.Wordlist(dataset.raw.joinpath(FNAME).as_posix(), col="counterpart_doculect")

    # get the language identifiers stored in wl._meta['doculect'] parsed from input file
    lids = {}
    for line in wl._meta['doculect']:
        rest = line.split(', ')
        name = rest.pop(0)
        lids[name] = rest.pop(0)

    concepts = {
        c['SPANISH'] + '_' + c['ENGLISH']:
        (c['CONCEPTICON_ID'], c['ENGLISH'], c['SPANISH'])
        for c in concepticon.conceptlist(dataset.conceptlist)}

    src = getSourceFromBibTex(SOURCE)
    citekey = list(src.entries.keys())[0]

    def grouped_rows(wl):
        rows = [
            (wl[k, 'doculect'], wl[k, 'concept'], wl[k, 'counterpart'], wl[k, 'qlcid'])
            for k in wl]
        return groupby(sorted(rows), key=lambda r: (r[0], r[1]))

    with CldfDataset((
            'ID',
            'Language_ID',
            'Language_name',
            'Language_iso',
            'Parameter_ID',
            'Parameter_name',
            'Parameter_Spanish_name',
            'Value',
            'Source',
            'QuantHistLing_ID'
            ),
            dataset) as ds:
        ds.sources.add(src)
        for (language, concept), rows in grouped_rows(wl):
            iso = lids[language]
            cid, ceng, cspa = concepts[concept.lower()]
            for i, (l, c, form, id_) in enumerate(rows):
                assert ds.add_row([
                    '%s-%s-%s-%s-%s' % (iso, slug(language), cid, slug(concept), i + 1),
                    dataset.glottocode_by_iso.get(iso, ''),
                    language.capitalize(),
                    iso,
                    cid,
                    ceng,
                    cspa,
                    form,
                    citekey,
                    id_
                ])
