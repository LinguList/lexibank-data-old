# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.providers import abvd
from pylexibank.util import get_reference

SECTION = 'bantu'


def download(dataset, **kw):
    abvd.download(dataset, SECTION)


def cldf(dataset, glottolog, concepticon, **kw):
    concept_map = {
        c['URL'].split('v=')[1]: c['CONCEPTICON_ID']
        for c in concepticon.conceptlist(dataset.conceptlist)}
    for c in dataset.concepts:
        concept_map[c['ID']] = c['CONCEPTICON_ID'] or None

    gl_map = {l.iso_code: l.id for l in glottolog.languoids() if l.iso_code}
    wordlists = []
    for xml in dataset.raw.glob('*.xml'):
        wl = abvd.Wordlist(dataset, xml, SECTION)
        if wl.language.iso:
            if wl.language.iso in gl_map:
                wl.language.glottocode = gl_map[wl.language.iso]
        if not wl.language.glottocode:
            dataset.log.warn(
                'no glottocode for language %s, iso-code %s' % (wl.language.name, wl.language.iso))
        wordlists.append(wl)

    sources = {}
    unmapped = dict(languages=set(), concepts=set())
    for wl in wordlists:
        args = [None, None]
        ref = get_reference(None, None, wl.language.notes, None, sources)
        if ref:
            args = [ref.source.id, ref.source]
        wl.to_cldf(concept_map, unmapped, *args)
    abvd.print_unmapped(unmapped)
