# coding: utf8
from __future__ import unicode_literals, print_function, division
from itertools import groupby

from six.moves.urllib.request import urlretrieve
from clldutils.dsv import UnicodeReader
from clldutils.misc import slug
from pycldf.sources import Source

from pylexibank.util import xls2csv, with_temp_dir
from pylexibank.dataset import CldfDataset, Unmapped
from pylexibank.lingpy_util import (clean_string, iter_alignments,
        wordlist2cognates, getEvoBibAsSource)
import lingpy as lp


URL = "https://zenodo.org/record/34092/files/Sidwell-Austroasiatic_phylogenetic-dataset-2015.xlsm"
SOURCE = 'Sidwell2015'


def download(dataset):
    with with_temp_dir() as tmpdir:
        urlretrieve(URL, tmpdir.joinpath('ds.xlsm').as_posix())
        xls2csv(tmpdir.joinpath('ds.xlsm'), outdir=dataset.raw)


def cldf(dataset, concepticon, **kw):
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

    glottolog = dataset.glottolog_languoids_by_iso
    glottolog.update({l['NAME']: l['GLOTTOCODE'] or None for l in dataset.languages})

    sources = {}
    for src, langs in groupby(
            sorted(languages.values(), key=lambda r: r[6]), lambda r: r[6]):
        langs = [l[1] for l in langs]
        src = Source('misc', '_'.join(map(slug, langs)), title=src)
        for lang in langs:
            sources[lang] = src
    sources['cognates'] = getEvoBibAsSource(SOURCE)

    unmapped = Unmapped()
    with CldfDataset((
            'ID',
            'Language_ID',
            'Language_name',
            'Language_iso',
            'Parameter_ID',
            'Parameter_name',
            'Value',
            'Segments',
            'Source',
            'Comment',
            ), dataset) as ds:
        ds.sources.add(*sources.values())
        D = {0: ['lid', 'doculect', 'concept', 'ipa', 'tokens', 'cog']}
        for i, row in enumerate(words):
            form = row[4]
            if not form or form in '*-':
                continue
            assert row[1] in concepticon
            lang = language_map.get(row[3], row[3].strip())
            assert lang in languages
            gc = glottolog.get(glottolog.get(languages[lang][7]), lang)
            if not gc:
                unmapped.languages.add(('', lang, languages[lang][7]))
            # get segments
            segments = clean_string(form)[0]
            # get cognate identifier
            cogid = row[5] if row[5].strip() and row[5].strip() != '*' else ('e%s' % i)
            cogid = row[1] + '-' + cogid
            lid = '{0}-{1}'.format(ds.name, i + 1)
            ds.add_row([
                lid,
                glottolog.get(lang, glottolog.get(languages[lang][7])),
                lang,
                languages[lang][7],
                concepticon[row[1]],
                row[1],
                form,
                segments,
                sources[lang].id,
                None
            ])
            D[i + 1] = [lid, lang, row[1], form, segments, cogid]
        wl = lp.Wordlist(D)
        wl.renumber('cog')
        alm = lp.Alignments(wl)
        dataset.cognates.extend(iter_alignments(alm, wordlist2cognates(wl, ds, SOURCE)))

    unmapped.pprint()
