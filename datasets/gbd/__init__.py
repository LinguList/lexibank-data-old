# coding: utf8
from __future__ import unicode_literals, print_function, division
from zipfile import ZipFile
from collections import OrderedDict
import re

from six.moves.urllib.request import urlretrieve
from clldutils.dsv import UnicodeReader
from clldutils.misc import slug

from pylexibank.util import split_by_year, get_reference, xls2csv, with_temp_dir
from pylexibank.dataset import CldfDataset, Unmapped
from pylexibank.lingpy_util import clean_string


NAME = 'Grollemund-et-al_Bantu-database_2015'
PAGES_PATTERN = re.compile('\s+p\.?\s*(?P<pages>[0-9]+)\.$')

TRANSCRIPTION_REPORT_CFG = {'column': 'Segments', 'segmentized': True}


def clean_string_with_validation(string):
    try:
        return ' '.join(clean_string(string))
    except IndexError:
        return None


def download(dataset):
    with with_temp_dir() as tmpdir:
        urlretrieve(
            'http://www.evolution.reading.ac.uk/Files/%s.zip' % NAME,
            tmpdir.joinpath('gbd.zip').as_posix())
        with ZipFile(tmpdir.joinpath('gbd.zip').as_posix()) as zip:
            zip.extract(NAME + '.xlsx', tmpdir.as_posix())
        xls2csv(tmpdir.joinpath(NAME + '.xlsx'), outdir=dataset.raw)


def get_ref(lang, sources):
    pages = None
    src = lang['source'].strip()
    if src.startswith('Collectors:'):
        src = lang['source'].split('Collectors:')[1].strip()

    match = PAGES_PATTERN.search(src)
    if match:
        pages = match.group('pages')
        src = src[:match.start()].strip()

    author, year, src = split_by_year(src)
    return get_reference(author, year, src, pages, sources)


def read_csv(dataset, type_):
    header, rows = None, []
    with UnicodeReader(dataset.raw.joinpath(NAME + '.' + type_ + '.csv')) as reader:
        for i, row in enumerate(reader):
            row = [c.strip() for c in row]
            if i == 2:
                header = row
            if i > 2:
                rows.append(row)
    return header, rows


def cldf(dataset, glottolog, concepticon, **kw):
    language_map = {l['NAME']: l['GLOTTOCODE'] or None for l in dataset.languages}
    concept_map = {
        c['ENGLISH']: c['CONCEPTICON_ID']
        for c in concepticon.conceptlist(dataset.conceptlist)}

    data = OrderedDict()

    # The english concept labels in the two excel sheets differ in one place:
    gloss_map = {'road/path': 'road'}

    header, rows = read_csv(dataset, 'Data')
    for row in rows:
        data[row[0]] = {
            'language': row[0],
            'source': row[-1],
            'items': OrderedDict(zip(header[1:-2], row[1:-2])),
        }

    ids = [slug(l['language']) for l in data.values()]
    assert len(set(ids)) == len(ids)

    header, rows = read_csv(dataset, 'Multistate')
    for row in rows:
        ldata = data[row[0]]
        for j, csid in enumerate(row[1:]):
            concept = header[j + 1]
            try:
                csid = '%s' % int(float(csid))
            except ValueError:
                assert csid == '?'
            ldata['items'][gloss_map.get(concept, concept)] = (
                ldata['items'][gloss_map.get(concept, concept)],
                csid)

    unmapped = Unmapped()
    sources = {}
    with CldfDataset((
                'ID',
                'Language_ID',
                'Language_name',
                'Parameter_ID',
                'Parameter_name',
                'Value',
                'Segments',
                'Source',
                'Cognacy',
            ), dataset) as ds:
        for lang in data.values():
            if not language_map[lang['language']]:
                unmapped.languages.add((lang['language'], lang['language'], ''))
            ref = ''
            if lang['source']:
                ref = get_ref(lang, sources)
                if ref:
                    ds.sources.add(ref.source)
                    ref = '%s' % ref

            for concept, item in lang['items'].items():
                if concept not in concept_map:
                    unmapped.concepts.add((slug(concept), concept))
                wid = '%s-%s' % (slug(lang['language']), slug(concept))
                
                if ds.add_row([
                    wid,
                    language_map[lang['language']],
                    lang['language'],
                    concept_map.get(concept),
                    concept,
                    item[0] if clean_string_with_validation(item[0]) else None,
                    clean_string_with_validation(item[0]),
                    ref,
                    item[1],
                ]) and item[1] != '?':
                        dataset.cognates.append([
                            wid,
                            ds.name,
                            item[0],
                            '%s-%s' % (slug(concept), item[1]),
                            False,
                            'expert',
                            '',
                            '',
                            '',
                            '',
                        ])
        dataset.write_cognates()
        unmapped.pprint()
