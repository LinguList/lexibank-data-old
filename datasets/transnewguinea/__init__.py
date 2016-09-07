# coding: utf8
from __future__ import unicode_literals, print_function, division
from itertools import groupby
from collections import Counter

from pycldf.sources import Source

from pylexibank.dataset import CldfDataset, Unmapped

from util import get_all, BASE_URL


def download(dataset):
    get_all(dataset, download_=True)


def cldf(dataset, concepticon, **kw):
    data = get_all(dataset)
    gl_map = {k: v.id for k, v in dataset.glottolog_languoids.items()}
    gl_map.update(dataset.glottocode_by_iso)

    swadesh_concepts = {
        k: v for k, v in data['word'].items() if v['id'] in data['concept_ids']}

    def normalized_gloss(gloss):
        if gloss.startswith('to '):
            gloss = gloss[3:].strip()
        if '/' in gloss:
            gloss = gloss.split('/')[0].strip()
        if '(' in gloss:
            gloss = gloss.split('(')[0].strip()
        if gloss.endswith('?'):
            gloss = gloss[:-1]
        return gloss

    swadesh2concepticon = {
        'right (hand)': '2183',
        'we incl. (pronoun d:1p, incl)': '1131',
        'left (hand)': '2182',
        'right (correct, true)': '1725',
        'in, inside': '1460',
        'to lie down': '215',
    }
    for conceptlist in [
        'Swadesh-1960-200',
        'Swadesh-1971-100',
        'Swadesh-1955-100',
        'Swadesh-1950-215',
        'Swadesh-1955-215'
    ]:
        for d in concepticon.conceptlist(conceptlist):
            swadesh2concepticon.setdefault(d['ENGLISH'], d['CONCEPTICON_ID'])

    concept_map = {}
    for concept in swadesh_concepts.values():
        gloss = normalized_gloss(concept['word'])
        if gloss in swadesh2concepticon:
            concept_map[concept['id']] = swadesh2concepticon[gloss]
        elif concept['word'] in swadesh2concepticon:
            concept_map[concept['id']] = swadesh2concepticon[concept['word']]
        else:
            raise ValueError(concept['word'])
    assert len(concept_map) == len(set(concept_map.values()))

    for c in dataset.concepts:
        if c['CONCEPTICON_ID']:
            concept_map[int(c['ID'])] = c['CONCEPTICON_ID'] or None

    uc = Counter()
    unmapped = Unmapped(lambda r: int(r[0]))
    for language_url, words in groupby(
            sorted(data['lexicon'].values(), key=lambda i: i['language']),
            lambda i: i['language']):
        contribution = data['language'][language_url]
        with CldfDataset((
                'ID',
                'Language_ID',
                'Language_iso',
                'Language_name',
                'Language_local_ID',
                'Parameter_ID',
                'Parameter_name',
                'Parameter_local_ID',
                'Value',
                'Source',
                'Cognate_Set',
                'Comment',
                'Loan',
                ), dataset, subset=contribution['id']) as ds:
            cname = contribution['language']
            if contribution['dialect']:
                cname += ' (%s Dialect)' % contribution['dialect']
            lid = gl_map.get(contribution['glottocode'])
            if not lid:
                lid = gl_map.get(contribution['isocode'])
                if not lid:
                    unmapped.languages.add(
                        (contribution['id'], cname, contribution['isocode']))
            if contribution['information']:
                ds.metadata['dc:description'] = contribution['information']

            ds.table.schema.aboutUrl = '%s.csv#{ID}' % ds.name
            ds.table.schema.columns['Loan'].datatype = 'boolean'
            ds.table.schema.columns['Parameter_local_ID'].valueUrl = \
                '%s/word/{Parameter_local_ID}' % BASE_URL
            ds.table.schema.columns['Language_local_ID'].valueUrl = \
                '%s/language/{Language_local_ID}' % BASE_URL

            for word in words:
                concept = data['word'][word['word']]
                if concept['id'] not in concept_map:
                    unmapped.concepts.add((concept['id'], concept['word']))
                    uc.update([concept['word']])
                src = data['source'].get(word['source'])
                if src:
                    ds.sources.add(Source(
                        'misc',
                        src['slug'],
                        author=src['author'],
                        year=src['year'],
                        transnewguinea_id=BASE_URL + '/source/' + src['slug'],
                        title=src['reference']))
                ds.add_row([
                    word['id'],
                    lid,
                    contribution['isocode'],
                    cname,
                    contribution['slug'],
                    concept_map.get(concept['id']),
                    concept['word'],
                    concept['slug'],
                    word['entry'],
                    src['slug'] if src else None,
                    None,
                    word['annotation'],
                    word['loan'],
                ])
    unmapped.pprint()
    #for k, v in uc.most_common(50):
    #    print(k, v)
