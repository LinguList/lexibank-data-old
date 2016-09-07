# coding: utf8
"""
Additional fields in lexical items:

Etymology Code 55255
Phonemicized Form 38754
Linnean Name 19416
Word Structure 16731
Psychotropic 13720
Medicinal 13720
Food Source 13720
Traded 13720
Ritual/Mythologically Significant 13720
Dangerous 13550
Etymology Notes 8646
Gloss as in Source 8544
Proto-Language 6525
Loan Source 6201
Distribution 4455
Word Structure Notes 3796
Proto-Form 3591
Range of Term 2533
Wanderwort Status 2326
Etyma Set 2316
How Collected 883
Classifier 873
Who Collects 846
How Prepared 841
Association with Social Categories 771
Habitat 685
Classifier Notes 623
Food Notes 487
Ritual Notes 327
Hypernym 196
Trade Notes 171
Medicinal Notes 89
Psychotropic Notes 8

"""
from __future__ import unicode_literals, print_function, division
import re
from itertools import groupby
from collections import defaultdict, Counter

from clldutils import jsonlib

from pylexibank.util import split
from pylexibank.dataset import CldfDataset

from .util import get, parse, path2name, VALUE_MAP, itersources


def download(dataset):
    for index, item, with_items in [
        ('languages', 'language', False),
        ('lexical', 'feature', True),
    ]:
        for a in get(dataset, '/' + index).find_all('a', href=True):
            if a['href'].startswith('/%s/%s/' % (index, item)):
                path = dataset.raw.joinpath(path2name(a['href'], ext='json'))
                if not path.exists():
                    parse(
                        get(dataset, a['href']),
                        a['href'].split('/')[-1],
                        path,
                        with_items=with_items)


missing_languages = ['45', '46']
missing_marker = [
    '?',
    '[missing]',
    'missing',
    '#NAME?',
    'X',
    '[absent]',
    '-',
    '--',
    '...'
]


def valid_Value(row):
    return bool(row['Value']) and row['Value'] not in missing_marker


def cldf(dataset, concepticon, **kw):
    concept_map = {
        re.sub('^(\*|\$)', '', c['ENGLISH']): c['CONCEPTICON_ID']
        for c in concepticon.conceptlist(dataset.conceptlist)}
    for c in dataset.concepts:
        concept_map[(c['ID'], c['GLOSS'])] = c['CONCEPTICON_ID'] or None
    language_map = {l['ID']: l['GLOTTOCODE'] or None for l in dataset.languages}

    concepts = []
    languages = {}
    for path in dataset.raw.glob('languages-language-*.json'):
        data = jsonlib.load(path)
        data['glottocode'] = language_map[data['id']]
        languages[data['id']] = data

    for path in sorted(
            dataset.raw.glob('lexical-feature-*.json'),
            key=lambda p: int(p.stem.split('-')[-1])):
        data = jsonlib.load(path)
        data['concepticon'] = concept_map.get(data['concept'])
        if not data['concepticon']:
            data['concepticon'] = concept_map[(data['id'], data['concept'])]
        concepts.append(data)

    fields = defaultdict(lambda: Counter())
    sources = {}
    with CldfDataset((
            'ID',
            'Language_ID',
            'Language_iso',
            'Language_name',
            'Language_local_ID',
            'Parameter_ID',
            'Parameter_name',
            'Parameter_local_ID',
            'Semantic_field',
            'Value',
            'Context',
            'Loan',
            'Phonemic',
            'Source',
            'Creator',
            'Comment',
            ), 
            dataset) as ds:
        ds.table.schema.columns['Loan'].datatype = 'boolean'
        ds.table.schema.columns['Parameter_local_ID'].valueUrl = \
            'https://huntergatherer.la.utexas.edu/lexical/feature/{Parameter_local_ID}'
        ds.table.schema.columns['Language_local_ID'].valueUrl = \
            'https://huntergatherer.la.utexas.edu/languages/language/{Language_local_ID}'

        for param in concepts:
            for lid, items in groupby(
                    sorted(param['items'], key=lambda i: i['Language']),
                    lambda i: i['Language']):
                lid = lid.split('/')[-1]
                if lid in missing_languages:
                    continue
                lang = languages[lid]
                i = 0
                for item in items:
                    form = item['Orthographic Form'].strip()
                    refs = [ref for ref in itersources(item, lang, sources) if ref]
                    ds.sources.add(*[ref.source for ref in refs])
                    for k, v in item.items():
                        if v:
                            fields[k].update([v])
                    for fform, context in split(form):
                        i += 1
                        ds.add_row([
                            '%s-%s-%s' % (lid, param['id'], i),
                            lang['glottocode'],
                            lang['ISO 639-3'],
                            lang['name'],
                            lang['id'],
                            param['concepticon'],
                            param['concept'],
                            param['id'],
                            param['Semantic Field'],
                            fform,
                            context,
                            bool(item['Loan Source'] or item['Wanderwort Status']),
                            item['Phonemicized Form'] or None,
                            ';'.join('%s' % ref for ref in refs),
                            item.get('Created By'),
                            item.get('General Notes'),
                        ])
    #print(fields['Loan Source'].most_common(5))
    #print(fields['Wanderwort Status'].most_common(5))
