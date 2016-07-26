# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.dataset import CldfDataset, REQUIRED_FIELDS
from pycldf.sources import Source
from pylexibank.util import with_temp_dir
from six.moves.urllib.request import urlretrieve
from clldutils.misc import slug
import zipfile
import shutil
import os

import lingpy as lp

URL = "https://zenodo.org/record/51328/files/partial-cognate-detection-v1.0.zip"
PATH = os.path.join('lingpy-partial-cognate-detection-2089b49', 'data')
DSETS = ['Bai-110-9.tsv', 'Tujia-109-5.tsv', 'Chinese-180-18.tsv']

SOURCES = {
        'Bai-110-9' : dict(
            Title = "Comparison of languages in contact. The distillation method and the case of Bai", 
            Publisher = "Institute of Linguistics Academia Sinica", 
            Year = "2006", 
            Author = "Wang, Feng",
            Address = "Taipei"),
        'Chinese-180-18' : dict(
            Title = "Xiàndài Hànyǔ Fāngyán Yīnkù [Phonological database of Chinese dialects]", 
            Publisher = "Shànghǎi Jiàoyù",
            Year = "2004",
            Author = "Hóu, Jīngyī",
            Address = "Shanghai"
            ),
        'Tujia-109-5' : dict(
            Title = "Annotated Swadesh wordlists for the Tujia group (Sino-Tibetan family)",
            Url = "http://starling.rinet.ru/new100/tuj.xls",
            Booktitle = "The Global Lexicostatistical Database",
            Author = "Starostin, George S.",
            Editor = "Starostin, George S.",
            Year = "2013"
            )
        }

def download(dataset, **kw):
    
    with with_temp_dir() as tmpdir:
        urlretrieve(URL, tmpdir.joinpath('ds.zip').as_posix())
        with zipfile.ZipFile(
                str(tmpdir.joinpath('ds.zip'))) as zipf:
            for dset in DSETS:
                path = os.path.join(PATH, dset)
                zipf.extract(path)
                shutil.copy(path, dataset.raw.as_posix())
        

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

    for dset in DSETS:
        wl = lp.Wordlist(dataset.dir.joinpath('raw', 'Bai-110-9.tsv').as_posix())
        
        # language ids
        lids = dict(zip(wl.cols, range(1, wl.width+1)))
        src = Source('book', dset[:-4], **SOURCES[dset[:-4]])
        
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
                        dset[:-4],
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
                            pidx = wl[k, 'partialids'].index(pid)
                            cogid = '-'.join([slug(wl[k, 'concept']), str(pid),
                                str(pidx)]) 
                            dataset.cognates.append([
                                k,
                                ds.name,
                                wl[k, 'ipa'],
                                cogid,
                                False
                                ])
            dataset.write_cognates()



