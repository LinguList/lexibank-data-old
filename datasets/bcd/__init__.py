# coding=utf-8
from __future__ import unicode_literals, print_function

from six import text_type
from clldutils.misc import slug
from clldutils.path import Path
import lingpy as lp

from pylexibank.dataset import CldfDataset
from pylexibank.lingpy_util import getEvoBibAsSource
from pylexibank.util import download_and_unpack_zipfiles

URL = "https://zenodo.org/record/16760/files/Network-perspectives-on-Chinese-dialect-history-1.zip"
PATH = Path('LinguList-Network-perspectives-on-Chinese-dialect-history-933bf29/Supplementary_Material_I/data/')
DSET = 'chinese.tsv'
SOURCE = 'Hamed2006'


def download(dataset, **kw):
    download_and_unpack_zipfiles(
        URL, dataset, *[PATH.joinpath(DSET), PATH.joinpath('old_chinese.csv')])


def cldf(dataset, concepticon, **kw):
    wl = lp.Wordlist(dataset.dir.joinpath('raw', DSET).as_posix())
    gcode = {x['NAME']: x['GLOTTOCODE'] for x in dataset.languages}
    ccode = {x['ENGLISH']: x['CONCEPTICON_ID'] for x in
             concepticon.conceptlist(dataset.conceptlist)}
    src = getEvoBibAsSource(SOURCE)
    src2 = getEvoBibAsSource('List2015d')

    with CldfDataset((
        'ID',
        'Language_ID',
        'Language_name',
        'Language_iso',
        'Parameter_ID',
        'Parameter_name',
        'Value',
        'Source',
        'Cognacy',
        )
            , dataset) as ds:
        
        ds.sources.add(src, src2)

        # store list of proto-form to cognate set
        p2c = {}

        for k in wl:
            ds.add_row([
                '{0}-{1}'.format(SOURCE, k),
                gcode[wl[k, 'doculect']],
                wl[k, 'doculect'],
                '',
                ccode[wl[k, 'concept']],
                wl[k, 'concept'],
                wl[k, 'ipa'],
                SOURCE,
                wl[k, 'COGID']
            ])
            dataset.cognates += [[
                '{0}-{1}'.format(SOURCE, k),
                ds.name,
                wl[k, 'ipa'],
                '-'.join([slug(wl[k, 'concept']), str(wl[k, 'cogid'])]),
                '', 
                'expert',
                SOURCE,
                '',
                '',
                ''
            ]]
            p2c[wl[k, 'proto']] = wl[k, 'cogid']
        idx = max([k for k in wl]) + 1
        for line in lp.csv2list(dataset.raw.joinpath('old_chinese.csv').as_posix()):
            for val in line[1].split(', '):
                ds.add_row((
                    '{0}-{1}'.format(SOURCE, idx),
                    'sini1245',
                    'Old Chinese',
                    '',
                    ccode[line[0]],
                    line[0],
                    val,
                    SOURCE,
                    p2c.get(val, val)
                ))
                dataset.cognates += [[
                    '{0}-{1}'.format(SOURCE, idx),
                    ds.name,
                    val,
                    '-'.join([slug(line[0]), text_type(p2c.get(val, val))]),
                    '',
                    'expert',
                    SOURCE,
                    '',
                    '',
                    '']]
                idx += 1
