# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.dataset import CldfDataset, REQUIRED_FIELDS
from pycldf.sources import Source
from pycldf.dataset import Dataset
from pylexibank.util import with_temp_dir
from six.moves.urllib.request import urlretrieve, urlopen
from clldutils.misc import slug
from clldutils.path import Path

from pylexibank.lingpy_util import getEvoBibAsSource,\
        download_and_unpack_zipfiles, test_sequences

import lingpy as lp

URL = "https://zenodo.org/record/51328/files/partial-cognate-detection-v1.0.zip"
PATH = Path('lingpy-partial-cognate-detection-2089b49', 'data').as_posix()
DSETS = ['Bai-110-9.tsv', 'Tujia-109-5.tsv', 'Chinese-180-18.tsv']
SOURCES = ['Wang2006', 'Starostin2013b', 'Hou2004']


def download(dataset, **kw):
    download_and_unpack_zipfiles(URL, dataset, *[Path(PATH, dset).as_posix() for
        dset in DSETS])

def cldf(dataset, glottolog, concepticon, **kw):
    """
    Implements the conversion of the raw data to CLDF dataset(s).

    :param dataset: provides access to the information in supplementary files as follows:\
     - the JSON object from `metadata.json` is available as `dataset.md`\
     - items from languages.csv are available as `dataset.languages`\
     - items from concepts.csv are available as `dataset.concepts`\
     - if a Concepticon conceptlist was specified in metadata.json, its ID is available\
       as `dataset.conceptlist`
    :param glottolog: a pyglottolog.api.Glottolog` instance.
    :param concepticon:  a pyconcepticon.api.Concepticon` instance.
    :param kw: All arguments passed on the command line.
    """

    for dset, srckey in zip(DSETS, SOURCES):
        wl = lp.Wordlist(dataset.dir.joinpath('raw', dset).as_posix())
        
        # language ids
        lids = dict(zip(wl.cols, range(1, wl.width+1)))
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
                        k,
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
            etd = wl.get_etymdict(ref='partialids')
            for pid, vals in etd.items():
                for val in vals:
                    if val:
                        for k in val:
                            # get partial_cognate-index
                            cogid = '-'.join([slug(wl[k, 'concept']), pid]) 
                            dataset.cognates.append([
                                k,
                                ds.name,
                                wl[k, 'ipa'],
                                cogid,
                                False
                                ])
            dataset.write_cognates()

def report(dataset):
    for dset in DSETS:
        ds = Dataset.from_file(Path(dataset.cldf_dir, 
            dataset.id+'-'+dset.split('-')[0]+'.csv'))
        test_sequences(ds, 'Segments', segmentized=True)

