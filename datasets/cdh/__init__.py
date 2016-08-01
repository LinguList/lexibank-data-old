# coding=utf-8
from __future__ import unicode_literals, print_function

from collections import defaultdict
from pylexibank.dataset import CldfDataset
from pycldf.dataset import Dataset
from clldutils.misc import slug
from clldutils.path import Path

from pylexibank.lingpy_util import getEvoBibAsSource, test_sequences
from pylexibank.util import download_and_unpack_zipfiles
import lingpy as lp

URL = "https://gist.github.com/LinguList/7481097/archive/036610e905af4ea7fbc3de01fa443d8b08f4c684.zip"
PATH = Path('7481097-036610e905af4ea7fbc3de01fa443d8b08f4c684')
DSET = 'basic.qlc'
SOURCE = 'Hou2004'


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

    wl = lp.Wordlist(dataset.dir.joinpath('raw', DSET).as_posix())

    # get language identifiers
    lids, cids, coords = {}, {}, {}
    for row in dataset.languages:
        language = row['NAME']
        lids[language] = row['GLOTTOCODE']
    coords = dict([wl.coords[taxon] for taxon in lids])
    modify = {'thunder (verb)' : 'thunder', 'flash (verb)': 'lightning',
            'room' : 'flat', 'have diarrea' : 'have diarrhoea', 
            'watery' : 'light'}
    for row in dataset.concepts:
        concept = modify[row['CONCEPT']] if row['CONCEPT'] in modify else \
                row['CONCEPT']
        cids[concept] = row['CONCEPT_SET']
    
    # language ids
    src = getEvoBibAsSource(SOURCE)

    # get partial identifiers
    partial_ids = defaultdict(list)
    partial_converter = {}
    idx = 1
    for k in wl:
        for char in wl[k, 'counterpart']:
            if char in partial_converter:
                pidx = partial_converter[char]
            else:
                pidx = idx
                partial_converter[char] = idx
                idx += 1
            partial_ids[k] += [pidx]
    
    with CldfDataset((
        'ID',
        'Language_ID',
        'Language_name',
        'Language_iso',
        'Parameter_ID',
        'Parameter_name',
        'Parameter_Chinese_name',
        'Value',
        'Value_Chinese_characters',
        'Source',
        'Segments',
        'Proto_form',
        'Middle_Chinese',
        'Cognacy',
        'Partial_cognacy',
        'Rank',
        'Comment'
        )
            , dataset) as ds:
        
        ds.sources.add(src)
        for k in wl:
            ds.add_row([
                    k,
                    lids[wl[k, 'doculect']],
                    wl[k, 'doculect'],
                    '',
                    cids[wl[k, 'concept']],
                    wl[k, 'concept'],
                    wl[k, 'mandarin'],
                    wl[k, 'ipa'],
                    wl[k, 'counterpart'],
                    SOURCE,
                    ' '.join(lp.ipa2tokens(wl[k, 'ipa'], merge_vowels=False,
                        expand_nasals=True)),
                    wl[k, 'proto'],
                    wl[k,'mch'],
                    wl[k, 'cogid'],
                    ' '.join([str(x) for x in partial_ids[k]]),
                    wl[k, 'order'],
                    wl[k, 'note'] if wl[k, 'note'] != '-' else '',
                    ])
        etd = wl.get_etymdict(ref='cogid')
        for pid, vals in etd.items():
            for val in vals:
                if val:
                    for k in val:
                        cogid = '-'.join([slug(wl[k, 'concept']), str(pid)]) 
                        dataset.cognates.append([
                            k,
                            ds.name,
                            wl[k, 'ipa'],
                            cogid,
                            False
                            ])
        dataset.write_cognates()

def report(dataset):
    ds = Dataset.from_file(Path(dataset.cldf_dir, 
        dataset.id+'.csv'))
    test_sequences(ds, 'Segments', segmentized=True)
    ds.write(dataset.cldf_dir)

