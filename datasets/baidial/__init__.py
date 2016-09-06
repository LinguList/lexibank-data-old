# coding=utf-8
from __future__ import unicode_literals, print_function

import lingpy as lp

from pylexibank.dataset import CldfDataset, TranscriptionReport
from pylexibank.lingpy_util import getEvoBibAsSource, clean_string

SOURCE = 'Allen2007'
DSET = 'Bai-Dialect-Survey.tsv'
TRANSCRIPTION_REPORT_CFG = dict(column='Segments', segmentized=True)


def download(dataset, **kw):
    pass


def cldf(dataset, glottolog, concepticon, **kw):
    wl = lp.Wordlist(dataset.dir.joinpath('raw', DSET).as_posix())
    gcode = {x['NAME']: x['GLOTTOCODE'] for x in dataset.languages}
    src = getEvoBibAsSource(SOURCE)

    with CldfDataset((
        'ID',
        'Language_ID',
        'Language_name',
        'Language_iso',
        'Parameter_ID',
        'Parameter_name',
        'Parameter_Chinese_name',
        'Value',
        'Segments',
        'Source'
        )
            , dataset) as ds:
        ds.sources.add(src)

        for k in wl:
            if wl[k, 'value'] not in '---' and wl[k, 'value'].strip():
                ds.add_row([
                    wl[k, 'lid'],
                    gcode[wl[k, 'doculect']],
                    wl[k, 'doculect'],
                    '',
                    wl[k, 'concepticon_id'],
                    wl[k, 'concept'],
                    wl[k, 'chinese'],
                    wl[k, 'value'],
                    clean_string(wl[k, 'value'])[0],
                    SOURCE
                ])
