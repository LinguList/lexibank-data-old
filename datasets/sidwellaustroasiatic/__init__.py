# coding: utf8
from __future__ import unicode_literals, print_function, division
from itertools import groupby

from six.moves.urllib.request import urlretrieve
from clldutils.dsv import UnicodeReader
from clldutils.misc import slug
from pycldf.sources import Source

from pylexibank.util import xls2csv, with_temp_dir
from pylexibank.dataset import CldfDataset, Unmapped


URL = "https://zenodo.org/record/34092/files/Sidwell-Austroasiatic_phylogenetic-dataset-2015.xlsm"


def download(dataset):
    with with_temp_dir() as tmpdir:
        urlretrieve(URL, tmpdir.joinpath('ds.xlsm').as_posix())
        xls2csv(tmpdir.joinpath('ds.xlsm'), outdir=dataset.raw)


def cldf(dataset, glottolog_, concepticon, **kw):
    concepticon = {
        c['ENGLISH']: c['CONCEPTICON_ID'] for c in
        concepticon.conceptlist(dataset.conceptlist)}
    concepticon['you (sing.)'] = concepticon['you (sing.) (thou)']
    concepticon['you (pl.)'] = concepticon['you (pl.) (ye)']
    concepticon['to itch/itchy'] = concepticon['to itch/to be itchy']
    concepticon['medicine'] = concepticon['medicine/juice']
    concepticon['excrement/shit'] = concepticon['feces/excrement/shit']

    language_map = {
        'Tampuon': 'Tampuan',
        'Palaung-Namhsan-Taunggyi': 'Palaung-Namhsan',
        'Jru-Laven\u02d0': 'Jru-Laven',
        'Pnar-Jaintia': 'Pnar',
        'K-Surin': 'Khmer-Surin',
    }

    languages = {}
    words = []

    with UnicodeReader(dataset.raw.joinpath('ds.Sheet1.csv')) as reader:
        for i, row in enumerate(reader):
            if 3 <= i < 125:
                languages[row[1]] = row
            elif i > 334:
                words.append(row)

    lids = [int(float(r[0])) for r in languages.values()]
    assert min(lids) == 1 and max(lids) == 122

    glottolog = {l['NAME']: l['GLOTTOCODE'] or None for l in dataset.languages}
    for l in glottolog_.languoids():
        if l.iso_code:
            glottolog[l.iso_code] = l.id

    sources = {}
    for src, langs in groupby(
            sorted(languages.values(), key=lambda r: r[6]), lambda r: r[6]):
        langs = [l[1] for l in langs]
        src = Source('misc', '_'.join(map(slug, langs)), title=src)
        for lang in langs:
            sources[lang] = src

    unmapped = Unmapped()
    with CldfDataset((
            'ID',
            'Language_ID',
            'Language_name',
            'Language_iso',
            'Parameter_ID',
            'Parameter_name',
            'Value',
            'Source',
            'Comment',
            ), dataset) as ds:
        ds.sources.add(*sources.values())
        for i, row in enumerate(words):
            form = row[4]
            if not form or form == '*':
                continue
            assert row[1] in concepticon
            lang = language_map.get(row[3], row[3].strip())
            assert lang in languages
            gc = glottolog.get(lang, glottolog.get(languages[lang][7]))
            if not gc:
                unmapped.languages.add(('', lang, languages[lang][7]))
            ds.add_row([
                '%s' % (i + 1,),
                glottolog.get(lang, glottolog.get(languages[lang][7])),
                lang,
                languages[lang][7],
                concepticon[row[1]],
                row[1],
                form,
                sources[lang].id,
                None,
            ])
    unmapped.pprint()
