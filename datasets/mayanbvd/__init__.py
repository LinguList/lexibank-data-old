# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.providers import abvd
from pylexibank.dataset import Unmapped

SECTION = 'mayan'


def download(dataset):
    abvd.download(dataset, SECTION)


def cldf(dataset, concepticon, **kw):
    language_map = {l['NAME']: l['GLOTTOCODE'] or None for l in dataset.languages}
    unmapped = Unmapped(lambda r: int(r[0]))
    wordlists = []
    for xml in dataset.raw.glob('*.xml'):
        wl = abvd.Wordlist(dataset, xml, SECTION)
        if wl.language.name in language_map:
            wl.language.glottocode = language_map[wl.language.name]
        elif wl.language.iso:
            if wl.language.iso in dataset.glottocode_by_iso:
                wl.language.glottocode = dataset.glottocode_by_iso[wl.language.iso]
        if not wl.language.glottocode:
            unmapped.languages.add((wl.language.id, wl.language.name, wl.language.iso))
        wordlists.append(wl)

    concept_map = {cs.gloss: cs.id for cs in concepticon.conceptsets.values()}
    concept_map.update({c['GLOSS']: c['CONCEPTICON_ID'] or None for c in dataset.concepts})
    for wl in wordlists:
        wl.to_cldf(concept_map, unmapped, concept_key=lambda entry: entry.word)
        dataset.cognates.extend(list(wl.cognates()))
    unmapped.pprint()
