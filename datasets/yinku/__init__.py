# coding=utf-8
from __future__ import unicode_literals, print_function

from collections import defaultdict
from pylexibank.dataset import CldfDataset
from clldutils.misc import slug
from clldutils.path import Path

from pylexibank.lingpy_util import getEvoBibAsSource, iter_alignments
from pylexibank.util import download_and_unpack_zipfiles
import lingpy as lp

URL = "https://gist.github.com/LinguList/7481097/archive/036610e905af4ea7fbc3de01fa443d8b08f4c684.zip"
PATH = Path('7481097-036610e905af4ea7fbc3de01fa443d8b08f4c684')
DSET = 'basic.qlc'
SOURCE = 'Hou2004'

TRANSCRIPTION_REPORT_CFG = {'column': 'Segments', 'segmentized': True}


def download(dataset, **kw):
    download_and_unpack_zipfiles(URL, dataset, PATH.joinpath(DSET))


def cldf(dataset, concepticon, **kw):
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

    wl = lp.Wordlist(dataset.raw.joinpath(DSET).as_posix())

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
    src2 = getEvoBibAsSource('List2014b')

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

    # trace if proto-langugages was visited
    visited = []
    idx = max([k for k in wl]) + 1
    
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
        'Cognacy',
        'Rank',
        'Comment'
        )
            , dataset) as ds:
        
        ds.sources.add(src)
        ds.sources.add(src2)

        D = {0 : ['doculect', 'concept', 'ipa', 'tokens', 'cogid']}
        for k in wl:
            tokens = lp.ipa2tokens(wl[k, 'ipa'], merge_vowels=False,
                    expand_nasals=True)
            # remove sandhi-annotation in tokens, as it is confusing clpa
            for i, t in enumerate(tokens):
                if '⁻' in t:
                    tokens[i] = t[:t.index('⁻')]
            ds.add_row([
                    '{0}-{1}'.format(SOURCE, k),
                    lids[wl[k, 'doculect']],
                    wl[k, 'doculect'],
                    '',
                    cids[wl[k, 'concept']],
                    wl[k, 'concept'],
                    wl[k, 'mandarin'],
                    wl[k, 'ipa'],
                    wl[k, 'counterpart'],
                    SOURCE,
                    ' '.join(tokens),
                    wl[k, 'cogid'],
                    wl[k, 'order'],
                    wl[k, 'note'] if wl[k, 'note'] != '-' else '',
                    ])
            D[k] = [wl[k, 'doculect'], wl[k, 'concept'], wl[k, 'ipa'], tokens, wl[k, 'cogid']]
            if wl[k, 'cogid'] not in visited:
                # we need to add new tones, otherwise it won't work, so we
                # split syllables first, then check if the syllable ends with
                # tone or not and add a '1' if this is not the case
                syllables = wl[k, 'mch'].split('.')
                for i, s in enumerate(syllables):
                    if s[-1] not in '²³':
                        if s[-1] not in 'ptk':
                            syllables[i] += '¹'
                        else:
                            syllables[i] += '⁴'
                tokens = lp.ipa2tokens(''.join(syllables))
                ds.add_row(['{0}-{1}'.format(wl[k, 'concept'], idx), 'sini1245', 'Middle Chinese', 
                    '', cids[wl[k, 'concept']], wl[k, 'concept'], '', 
                    wl[k, 'proto'], wl[k, 'counterpart'], SOURCE, ' '.join(tokens),
                    wl[k, 'cogid'], '', ''])
                D[idx] = ['Middle Chinese', wl[k, 'concept'], wl[k, 'mch'], tokens, wl[k, 'cogid']]
                idx += 1
                visited += [wl[k, 'cogid']]
        alms = lp.Alignments(D)
        cognates = [[
            '{0}-{1}'.format(SOURCE, k),
            ds.name,
            alms[k, 'ipa'],
            '-'.join([slug(alms[k, 'concept']), str(alms[k, 'cogid'])]),
            '',
            'expert',
            SOURCE,
            '', '', ''] for k in alms]

        dataset.cognates.extend(iter_alignments(alms, cognates,
            method='library'))
