# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.providers import abvd
from pylexibank.util import get_reference
from pylexibank.dataset import Unmapped

SECTION = 'bantu'


def download(dataset, **kw):
    abvd.download(dataset, SECTION)


def cldf(dataset, concepticon, **kw):
    concept_map = {
        c.attributes['url'].split('v=')[1]: c.concepticon_id
        for c in dataset.conceptlist.concepts.values()}
    for c in dataset.concepts:
        concept_map[c['ID']] = c['CONCEPTICON_ID'] or None

    gl_map = dataset.glottocode_by_iso
    wordlists = []
    for xml in dataset.raw.glob('*.xml'):
        wl = abvd.Wordlist(dataset, xml, SECTION)
        if wl.language.iso:
            if wl.language.iso in gl_map:
                wl.language.glottocode = gl_map[wl.language.iso]
        if not wl.language.glottocode:
            dataset.log.warn(
                'no glottocode for language %s, iso-code %s' % (
                    wl.language.name, wl.language.iso))
        wordlists.append(wl)

    sources = {}
    unmapped = Unmapped(lambda r: int(r[0]))
    for wl in wordlists:
        args = [None, None]
        ref = get_reference(None, None, wl.language.notes, None, sources)
        if ref:
            args = [ref.source.id, ref.source]
        wl.to_cldf(concept_map, unmapped, *args)
    unmapped.pprint()
