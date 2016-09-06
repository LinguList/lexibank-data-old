# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.dataset import CldfDataset
from pylexibank.util import download_and_unpack_zipfiles
from clldutils.misc import slug
from clldutils.path import Path
from pylexibank.lingpy_util import getEvoBibAsSource, iter_alignments
import lingpy as lp

URL = "https://zenodo.org/record/11880/files/germanic.zip"
PATH = Path("Germanic/msa/")
FILES = list(range(369, 480))
languages = {
    "English": "stan1293",
    "Danish": "dani1285",
    "Dutch": "dutc1256",
    "Faroese": "faro1244",
    "German": "stan1295",
    "Icelandic": "icel1247",
    "Norwegian (Stavanger)": "norw1258",
    "Yiddish (New York)": "west2361",
    "West Frisian (Grou)": "west2354"
}
TRANSCRIPTION_REPORT_CFG = dict(column='Segments', segmentized=True)


def download(dataset, **kw):
    download_and_unpack_zipfiles(
        URL,
        dataset,
        *[PATH.joinpath('phonalign_{0}.msa'.format(i)) for i in range(369, 480)])


def cldf(dataset, glottobank, concepticon, **kw):
    concepts = {x['GLOSS']: x['CONCEPTICON_ID'] for x in dataset.concepts}
    D = {}  # dictionary to be passed to lingpy
    D[0] = ['doculect', 'glottolog', 'concept', 'concepticon', 'ipa', 'segments', 'cogid', 'alignment']
    idx = 1
    for f in FILES:
        msa = lp.MSA(dataset.raw.joinpath('phonalign_{0}.msa'.format(f)).as_posix())
        concept = msa.seq_id[1:-1] # strip quotation marks from concept
        cid = concepts.get(concept, '')
        for i, taxon in enumerate(msa.taxa):
            if taxon in languages:
                tid = languages[taxon]
                alignment = ' '.join(msa.alignment[i])
                tokens = ' '.join([x for x in msa.alignment[i] if x != '-'])
                ipa = tokens.replace(' ','')
                cogid = '{0}-{1}'.format(concept, f)
                D[idx] = [taxon, tid, concept, cid, ipa, tokens, cogid,
                        alignment]
                idx += 1

    with CldfDataset((
            'ID',
            'Language_ID',
            'Language_name',
            'Language_iso',
            'Parameter_ID',
            'Parameter_name',
            'Value',
            'Segments',
            'Cognacy',
            'Source'
            )
                , dataset) as ds:
        src = getEvoBibAsSource('Heggarty2007')
        ds.sources.add(src)
        src = getEvoBibAsSource('List2014e')
        ds.sources.add(src)

        alm = lp.Alignments(D)
        for k in alm:
            ds.add_row(
                    ['Heggarty2007-{0}'.format(k)] + [alm[k, x] or '' for x in ['glottolog', 'taxon',
                        'iso', 'concepticon', 'concept', 'ipa']] + \
                                [' '.join(alm[k, 'tokens']), alm[k, 'cogid'], 'Heggarty2007']
                                )
            dataset.cognates += [[
                'Heggarty2007-{0}'.format(k),
                ds.name,
                alm[k, 'ipa'],
                alm[k, 'cogid'],
                '', 'expert', 'Heggarty2007', alm[k, 'alignment'],
                'expert', 'List2014e']]
        dataset.write_cognates()
