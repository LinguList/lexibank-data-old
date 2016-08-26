# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.dataset import CldfDataset
from clldutils.misc import slug
from clldutils.path import Path

from pylexibank.lingpy_util import getEvoBibAsSource, test_sequences 
        
from six.moves.urllib.request import urlretrieve

import lingpy as lp

URL = "http://edictor.digling.org/triples/get_data.py?file=tukano"
SOURCES = ['Chacon2014', 'Chacon2015']
abbr2lang = {'Bar': ('Bar', 'bao'), 'Bas': ('Barasano', 'bsn'), 'Des': ('Desano', 'des'), 'ID': ('Name', 'ISOCODE'), 'Kar': ('Karapan', 'coe'), 'Kor': ('Koreguahe', 'coe'), 'Kub': ('Kubeo', 'cub'), 'Kue': ('Kueretu', ''), 'Mai': ('Maihiki', 'ore'), 'Mak': ('Makuna', 'myy'), 'Pir': ('Piratapuyo', 'pir'), 'Pis': ('Pisamira', ''), 'Sek': ('Sekoya', 'sey'), 'Sio': ('Siona', 'snn'), 'Sir': ('Siriano', 'sri'), 'Tan': ('Tanimuka', 'tnc'), 'Tat': ('Tatuyo', 'tav'), 'Tuk': ('Tukano', 'tuo'), 'Tuy': ('Tuyuka', 'tue'), 'Wan': ('Wanano', 'gvc'), 'Yup': ('Yupua', ''), 'Yur': ('Yuruti', 'yur'), '*PT' : ('Proto-Tucanoan', 'tuca1253')}
for k in sorted(abbr2lang):
    abbr2lang[k.upper()] = abbr2lang[k]


def download(dataset, **kw):
    urlretrieve(URL, Path(dataset.raw, 'tukano.tsv').as_posix())

def cldf(dataset, glottolog, concepticon, **kw):
    
    wl = lp.Alignments(dataset.raw.joinpath('tukano.tsv').as_posix())
    src1 = getEvoBibAsSource('Chacon2014')
    src2 = getEvoBibAsSource('Chacon2015')
    gloss2conc = dict([(b,c) for a, b, c in dataset.concepts])
    cogid2proto = {}
    iso2gc = {l.iso: l.id for l in glottolog.languoids() if l.iso}

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
        'Cognacy',
        ), dataset) as ds:
        
        ds.sources.add(src1)
        ds.sources.add(src2)
        for k in wl:
            lid = wl[k, 'language']
            cogid = wl[k, 'cogid']
            concept = wl[k, 'concept']
            segments = wl[k, 'tokens']
            value = wl[k, 'ipa']
            cogid = wl[k, 'cogid']
            alignment = wl[k, 'alignment']
            name, iso = abbr2lang[lid]
            concept = wl[k, 'concept']
            cid = cogid2proto.get(concept, '')
            ds.add_row((
                'Chacon2014-'+str(k), iso2gc.get(lid, ''), name, iso, cid, concept, value, 'Chacon2014',
                ' '.join(segments), str(cogid)))
            
            cogid = '-'.join([slug(wl[k, 'concept']), '%s' % cogid])
            dataset.cognates.append([
                'Chacon2014-'+str(k),
                ds.name,
                wl[k, 'ipa'],
                cogid,
                '',
                'expert', 
                'Chacon2014',
                alignment,
                'expert',
                'Chacon2015'
                ])
        dataset.write_cognates()


def report(dataset):
    for ds in dataset.iter_cldf_datasets():
        test_sequences(ds, 'Segments', segmentized=True)
        ds.write(dataset.cldf_dir)

