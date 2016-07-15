# coding=utf-8
from __future__ import unicode_literals, print_function
from collections import defaultdict

from clldutils.misc import slug

from pylexibank.providers import abvd

from author_notes_map import MAP

SECTION = 'austronesian'


def download(dataset, **kw):
    abvd.download(dataset, SECTION)


def cldf(dataset, glottolog, concepticon, **kw):
    concept_map = {
        c['URL'].split('v=')[1]: c['CONCEPTICON_ID']
        for c in concepticon.conceptlist(dataset.conceptlist)}

    l_map = {int(l['ID']): l['GLOTTOCODE'] for l in dataset.languages if l['GLOTTOCODE']}
    assert 957 in l_map
    gl_map = {l.iso_code: l.id for l in glottolog.languoids() if l.iso_code}
    wordlists = []
    for xml in dataset.raw.glob('*.xml'):
        wl = abvd.Wordlist(dataset, xml, SECTION)
        if int(wl.language.id) in l_map:
            wl.language.glottocode = l_map[int(wl.language.id)]
        elif wl.language.iso:
            if wl.language.iso in gl_map:
                wl.language.glottocode = gl_map[wl.language.iso]
        wordlists.append(wl)

    source_map = defaultdict(lambda: (None, None))
    for wlid, (author, notes) in MAP.items():
        source_map[wlid.split('-', 1)[1]] = (slug(author), notes.strip())

    for wl in wordlists:
        wl.to_cldf(concept_map, *source_map[wl.id])
        dataset.cognates.extend(list(wl.cognates()))
