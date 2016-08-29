# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.dataset import CldfDataset
from clldutils.misc import slug
from clldutils.path import Path

from pylexibank.lingpy_util import getEvoBibAsSource, iter_alignments
from pylexibank.util import download_and_unpack_zipfiles
import lingpy as lp

URL = "https://zenodo.org/record/51328/files/partial-cognate-detection-v1.0.zip"
PATH = Path('lingpy-partial-cognate-detection-2089b49', 'data')
DSETS = ['Bai-110-9.tsv', 'Tujia-109-5.tsv', 'Chinese-180-18.tsv']
SOURCES = ['Wang2006', 'Starostin2013b', 'Hou2004']

TRANSCRIPTION_REPORT_CFG = {'column': 'Segments', 'segmentized': True}


def download(dataset, **kw):
    download_and_unpack_zipfiles(URL, dataset, *[PATH.joinpath(dset) for dset in DSETS])


def cldf(dataset, glottolog, concepticon, **kw):

    for dset, srckey in zip(DSETS, SOURCES):
        wl = lp.Wordlist(dataset.dir.joinpath('raw', dset).as_posix())
        src = getEvoBibAsSource(srckey)

        with CldfDataset((
            'ID',
            'Language_ID',
            'Language_name',
            'Language_iso',
            'Parameter_ID',
            'Parameter_name',
            'Value',
            'Source',
            'Segments',
            'CLPA',
            'Cognacy',
            'Partial_cognacy'
            )
                , dataset, subset=dset.split('-')[0]) as ds:
            
            ds.sources.add(src)
            for k in wl:
                ds.add_row([
                        '{0}-{1}'.format(srckey, k),
                        wl[k, 'glottolog'],
                        wl[k, 'doculect'],
                        '',
                        wl[k, 'concepticon_id'],
                        wl[k, 'concept'],
                        wl[k, 'ipa'],
                        srckey,
                        ' '.join(wl[k, 'tokens']),
                        ' '.join(wl[k, 'clpa']),
                        wl[k, 'cogid'],
                        ' '.join([str(x) for x in wl[k, 'partialids']])
                        ])
            cognates = []
            for k in wl:
                concept = wl[k, 'concept']
                idf = '-'.join([slug(concept), '%s' % wl[k, 'cogid']])
                cognates += [[
                    '{0}-{1}'.format(srckey, k),
                    ds.name,
                    wl[k, 'ipa'], 
                    idf, 
                    '', 
                    'expert',
                    srckey, 
                    '', 
                    '', 
                    ''
                ]]

            dataset.cognates.extend(iter_alignments(wl, cognates,
                method='progressive', prefix=srckey + '-'))
