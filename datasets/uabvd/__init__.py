# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.providers import abvd
from pylexibank.dataset import Unmapped

SECTION = 'utoaztecan'


def download(dataset):
    abvd.download(dataset, SECTION)


def cldf(dataset, glottolog, concepticon, **kw):
    gl_map = {l.iso_code: l.id for l in glottolog.languoids() if l.iso_code}
    l_map = {l['NAME']: l['GLOTTOCODE'] or None for l in dataset.languages}

    unmapped = Unmapped(lambda r: int(r[0]))
    wordlists = []
    for xml in dataset.raw.glob('*.xml'):
        wl = abvd.Wordlist(dataset, xml, SECTION)
        if wl.language.name in l_map:
            wl.language.glottocode = l_map[wl.language.name]
        elif wl.language.iso:
            if wl.language.iso in gl_map:
                wl.language.glottocode = gl_map[wl.language.iso]
        if not wl.language.glottocode:
            unmapped.languages.add((wl.language.id, wl.language.name, wl.language.iso))
        wordlists.append(wl)

    concept_map = {cs['GLOSS'].lower(): cs['ID'] for cs in concepticon.conceptsets()}
    concept_map.update({c['GLOSS']: c['CONCEPTICON_ID'] or None for c in dataset.concepts})

    for wl in wordlists:
        wl.to_cldf(
            concept_map,
            unmapped,
            concept_key=lambda entry: entry.word.split('/')[0])
        dataset.cognates.extend(list(wl.cognates()))
    unmapped.pprint()
