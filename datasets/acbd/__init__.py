# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.dataset import CldfDataset
from pylexibank.util import download_and_unpack_zipfiles
from clldutils.path import Path
from pylexibank.lingpy_util import getEvoBibAsSource, iter_alignments
import lingpy as lp

URL = "https://github.com/SequenceComparison/SupplementaryMaterial/zipball/master"
PATH = Path('SequenceComparison-SupplementaryMaterial-cc4bf85/benchmark/cognates/')
DSETS = ['SLV.csv', 'SIN.csv', 'ROM.csv', 'PIE.csv', 'PAN.csv', 'OUG.csv',
        'KSL.csv', 'JAP.csv', 'IEL.csv', 'IDS.csv', 'GER.csv', 'BAI.csv']
sources = ['Starostin2005b', 'Hou2004', 'Starostin2005b', 'Starostin2005b',
        'Greenhill2008', 'Zhivlov2011', 'Kessler2001', 'Hattori1973', 'Dunn2012', 'List2014c',
        'Starostin2005', 'Wang2006']

correct_languages = {
        "Guixian" : "Guiyang",
        "Berawan (Long Terawan)" : "Berawan_Long_Terawan",
        "Merina (Malagasy)" : "Merina_Malagasy"
        }
correct_concepts = {
        "ear 1" : "ear",
        "i" : "I",
        "lie 1" : "lie", 
        "light" : "watery",
        "soja sauce" : "soya sauce",
        "two pairs" : "two ounces",
        "walk (go)" : "walk(go)",
        "warm (hot)" : "warm",
        "gras" : "grass", 
        "saliva (splits)" : "saliva (spit)"
        }
        

def download(dataset, **kw):
    download_and_unpack_zipfiles(URL, dataset, *[PATH.joinpath(dset) for dset \
            in DSETS])


def cldf(dataset, glottolog, concepticon, **kw):
    gloss2con = {x['GLOSS']: x['CONCEPTICON_ID'] for x in dataset.concepts}
    lang2glot = {x['NAME']: x['GLOTTOCODE'] for x in dataset.languages}

    for dset, srckey in zip(DSETS, sources):
        wl = lp.Wordlist(dataset.raw.joinpath(dset).as_posix())
        if not 'tokens' in wl.header:
            wl.add_entries('tokens', 'ipa', lp.ipa2tokens, merge_vowels=False,
                    expand_nasals=True)
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
            'Cognacy',
            'Loan'
            )
                , dataset, subset=dset.split('.')[0]) as ds:
            ds.sources.add(src)
            errors = []
            cognates = []
            for k in wl:
                concept = wl[k, 'concept']
                if '(V)' in concept:
                    concept = concept[:-4]
                concept = correct_concepts.get(concept, concept)
                if concept not in gloss2con:
                    errors += [concept]
                doculect = correct_languages.get(wl[k, 'doculect'], wl[k, 'doculect'])
                loan = wl[k, 'cogid'] < 0
                cogid = abs(wl[k, 'cogid'])

                ds.add_row([
                    '{0}-{1}'.format(srckey, k),
                    lang2glot[doculect],
                    wl[k, 'glottolog'],
                    '',
                    gloss2con.get(wl[k, 'concept'], ''),
                    wl[k, 'concept'],
                    wl[k, 'ipa'],
                    srckey,
                    ' '.join(wl[k, 'tokens'] or ['']),
                    cogid,
                    wl[k, 'loan']
                    ])

                cognates += [[
                    '{0}-{1}'.format(srckey, k),
                    ds.name,
                    wl[k, 'ipa'],
                    cogid,
                    'borrowed' if loan else '',
                    'expert',
                    srckey,
                    '',
                    '',
                    ''
                    ]]

            dataset.cognates.extend(
                iter_alignments(lp.Alignments(wl), cognates, method='library'))
            for er in sorted(set(errors)):
                print(er, dset)
