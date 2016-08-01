# coding=utf-8
from __future__ import unicode_literals, print_function

from collections import defaultdict
from pylexibank.dataset import CldfDataset
from pycldf.dataset import Dataset
from clldutils.misc import slug
from clldutils.path import Path

from pylexibank.lingpy_util import getEvoBibAsSource,\
        download_and_unpack_zipfiles, test_sequences,\
        getSourceFromBibTex

import lingpy as lp

URL = "http://www.quanthistling.info/data/downloads/csv/data.zip"
PATH = Path('')
DSET = 'huber1992.csv'
SOURCE = """@book{Huber1992,author={Huber, Randall Q. and Reed, Robert B.},
title={Comparative vocabulary. Selected words in indigenous languages of
Columbia.}, address={Santafé de Bogotá}, publisher={Instituto lingüístico de
Veterano}}"""
SOURCE_KEY="Huber1992"

def download(dataset, **kw):
    download_and_unpack_zipfiles(URL, dataset, PATH.joinpath(DSET))


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
    
    # column "counterpart_doculect" gives us the proper names of the doculects
    wl = lp.Wordlist(dataset.dir.joinpath('raw', DSET).as_posix(), 
            col="counterpart_doculect")

    # get the language identifiers stored in wl._meta['doculect'] parsed from
    # input file
    lids = {}
    for line in wl._meta['doculect']:
        name, iso, *rest = line.split(', ')
        lids[name] = iso
    cid = {}
    cgl = {}
    for row in dataset.concepts:
        cid[row['SPANISH'] + '_'+row['ENGLISH']] = row['CONCEPTICON_ID']
        cgl[row['SPANISH'] + '_'+row['ENGLISH']] = [row['ENGLISH'], row['SPANISH']]

    # language ids
    src = getSourceFromBibTex(SOURCE)
    
    # correct qlc-ids
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
        )
            , dataset) as ds:
        
        ds.sources.add(src)
        errors = 0
        for k in wl:
            if ds.add_row([
                    k,
                    '',
                    wl[k, 'doculect'].capitalize(),
                    lids[wl[k, 'doculect']],
                    cid[wl[k, 'concept'].lower()],
                    cgl[wl[k, 'concept'].lower()][0],
                    cgl[wl[k, 'concept'].lower()][1],
                    wl[k, 'counterpart'],
                    SOURCE_KEY,
                    wl[k, 'qlcid']
                    ]):
                pass
            else:
                errors += 1

def report(dataset):
    ds = Dataset.from_file(Path(dataset.cldf_dir, 
        dataset.id+'.csv'))

