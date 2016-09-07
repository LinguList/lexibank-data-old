# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.providers import clld
from pylexibank.dataset import CldfDataset, Unmapped
from pylexibank.util import split


def download(dataset):
    clld.download(dataset, __name__)


def cldf(dataset, concepticon, **kw):
    concept_map = {cs['GLOSS']: cs['ID'] for cs in concepticon.conceptsets()}
    for concept in dataset.concepts:
        concept_map[concept['GLOSS']] = concept['CONCEPTICON_ID']
    language_map = {l['ID']: l['GLOTTOCODE'] or None for l in dataset.languages}

    unmapped = Unmapped(lambda r: r[1])

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
            'Context',
            'Source',
            'Comment',
            ), dataset) as ds:
        for ods in clld.itercldf(dataset, __name__):
            for row in ods.rows:
                if not row['Language_glottocode']:
                    if row['Language_ID'] in language_map:
                        row['Language_glottocode'] = language_map[row['Language_ID']]
                    else:
                        unmapped.languages.add((
                            row['Language_ID'], row['Language_name'], row['Language_iso']
                        ))
                for ref in row.refs:
                    ds.sources.add(ref.source)
                if row['Parameter_name'].upper() not in concept_map:
                    unmapped.concepts.add((row['Parameter_ID'], row['Parameter_name']))
                for i, (form, context) in enumerate(split(row['Value'])):
                    ds.add_row([
                        '%s-%s' % (row['ID'], i + 1),
                        row['Language_glottocode'],
                        row['Language_iso'],
                        row['Language_name'],
                        row['Language_ID'],
                        concept_map.get(row['Parameter_name'].upper()),
                        row['Parameter_name'],
                        row['Parameter_ID'],
                        form,
                        context,
                        row['Source'],
                        row['Comment'],
                    ])
    unmapped.pprint()
