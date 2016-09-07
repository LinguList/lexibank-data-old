# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.dsv import UnicodeReader

from pylexibank.util import xls2csv
from pylexibank.dataset import CldfDataset, valid_Value as vv_base
from pylexibank.lingpy_util import clean_string, iter_alignments, getEvoBibAsSource
import lingpy as lp


TRANSCRIPTION_REPORT_CFG = dict(column='Segments', segmentized=True)


def download(dataset):
    xls2csv(dataset.raw.joinpath('Semitic.Wordlists.xls'), outdir=dataset.raw)
    xls2csv(dataset.raw.joinpath('Semitic.Codings.Multistate.xlsx'), outdir=dataset.raw)


def valid_Value(row):
    return vv_base(row) and row['Value'] != '---'


def cldf(dataset, concepticon, **kw):
    concepticon = {
        c['ENGLISH']: c['CONCEPTICON_ID']
        for c in concepticon.conceptlist(dataset.conceptlist)}

    language_map = {l['NAME']: l['GLOTTOCODE'] or None for l in dataset.languages}

    header, rows = None, []
    with UnicodeReader(
            dataset.raw.joinpath('Semitic.Wordlists.ActualWordlists.csv')) as reader:
        for i, row in enumerate(reader):
            row = [c.strip() for c in row]
            if i == 0:
                header = row
            if i > 0:
                rows.append(row)
    cheader, crows = None, []
    with UnicodeReader(
            dataset.raw.joinpath('Semitic.Codings.Multistate.Sheet1.csv')) as reader:
        for i, row in enumerate(reader):
            row = [c.strip() for c in row]
            if i == 0:
                cheader = row
            if i > 0:
                crows.append(row)

    langs = header[1:]
    clean_langs = {
            """Gɛ'ɛz""": "Ge'ez",
            "Tigrɛ" : "Tigre",
            'ʷalani' : "Walani",
            "Ogadɛn Arabic" : "Ogaden Arabic",
            "Mɛhri" : "Mehri",
            "Gibbali" : "Jibbali",
            }
    correct_concepts = {
            'Cold (air)' : 'Cold (of air)',
            }
    src = getEvoBibAsSource('Kitchen2012')

    with CldfDataset((
            'ID',
            'Language_ID',
            'Language_name',
            'Parameter_ID',
            'Parameter_name',
            'Value',
            'Segments'
            ),
            dataset) as ds:
        D = {0 : ['doculect', 'concept', 'ipa', 'tokens']}
        idx = 1
        ds.sources.add(src)
        for row in rows:
            concept = row[0]
            for i, col in enumerate(row[1:]):
                lang = langs[i]
                if col != '---':
                    cleaned_string = clean_string(col, merge_vowels=True,
                            preparse=[("'", "ˈ"), ('?', "ʔ"), ('//', '/'),
                            ('', ''), ('7', 's'),
                            ('', '')])[0]
                    ds.add_row([
                        'Kitchen2012-'+str(idx),
                        language_map[lang],
                        clean_langs.get(lang, lang),
                        concepticon[concept],
                        concept,
                        col,
                        cleaned_string 
                    ])
                    D[idx] = [clean_langs.get(lang, lang), concept, col, cleaned_string]
                    idx += 1
        
        wl = lp.Wordlist(D)
        id2cog = {}
        errors = []
        for row in crows:
            taxon = row[0]
            for i, (concept, cog) in enumerate(zip(cheader[1:], row[1:])):
                nconcept = rows[i][0]
                if cog != '-':
                    idxs = wl.get_dict(taxon=taxon)
                    if idxs.get(nconcept, ''):
                        id2cog[idxs[nconcept][0]] = concept + '-' + cog
                    else:
                        errors += [(concept, nconcept, taxon)]
        bad_cogs = 1
        cognates = []
        for k in wl:
            cognates = []
            if k in id2cog:
                cogid = id2cog[k]
            else:
                cogid = str(bad_cogs)
                bad_cogs += 1
                id2cog[k] = cogid

        wl.add_entries('cog', id2cog, lambda x: x)
        wl.renumber('cog')
        for k in wl:
            cognates += [[
                'Kitchen2012-'+str(k),
                ds.name,
                wl[k, 'ipa'],
                wl[k, 'concept']+'-'+str(wl[k, 'cogid']),
                '',
                'expert',
                'Kitchen2012', 
                '', '', '']]

        dataset.cognates.extend(iter_alignments(lp.Alignments(wl), cognates))
