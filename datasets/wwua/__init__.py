# coding: utf8
from __future__ import unicode_literals, print_function, division

from six.moves.urllib.request import urlretrieve
from clldutils.dsv import UnicodeReader
from clldutils.misc import slug

from pylexibank.util import with_temp_dir, xls2csv
from pylexibank.dataset import CldfDataset

from pylexibank.lingpy_util import (
    clean_string, iter_cognates, iter_alignments, getEvoBibAsSource,
)

URL = "http://onlinelibrary.wiley.com/store/10.1111/cla.12078/asset/supinfo/cla12078-sup-0006-supinfo6.xls?v=1&s=4c895c80efa148e7872c3c7702c5df3ed192c236"
FILENAME = "cla12078-sup-0006-supinfo6.xls"
SOURCE = 'Wheeler2014'

TRANSCRIPTION_REPORT_CFG = {'column': 'Segments', 'segmentized': True}


def download(dataset):
    with with_temp_dir() as tmpdir:
        urlretrieve(URL, tmpdir.joinpath(FILENAME).as_posix())
        xls2csv(tmpdir.joinpath(FILENAME), outdir=dataset.raw)


def iterforms(s):
    for i, form in enumerate(s.split('|')):
        yield i + 1, form.strip().replace('\xad', '')


def cldf(dataset, glottolog, concepticon, **kw):
    concepticon = {
        c['ENGLISH']: c['CONCEPTICON_ID']
        for c in concepticon.conceptlist(dataset.conceptlist)}

    language_map = {l['NAME']: l['GLOTTOCODE'] or None for l in dataset.languages}

    with UnicodeReader(dataset.raw.joinpath(FILENAME.replace('xls', 'Sheet1.csv'))) as r:
        rows = [row for row in r]

    concepts = [
        (i, rows[0][i].replace('_', ' ').strip()) for i in range(1, len(rows[0]), 2)]
    assert all(concept in concepticon for _, concept in concepts)

    with CldfDataset((
            'ID',
            'Language_ID',
            'Language_name',
            'Parameter_ID',
            'Parameter_name',
            'Value',
            'Segments',
            'Source'
            ), dataset) as ds:
        ds.table.schema.columns['Value']['dc:format'] = 'IPA'
        ds.sources.add(getEvoBibAsSource(SOURCE))

        for row in rows[3:]:
            row = [col.strip() for col in row]
            if not row[0]:
                continue
            lname = row[0]
            for i, concept in concepts:
                for j, form in iterforms(row[i]):
                    if form != '?' and form.strip():
                        ds.add_row([
                            '%s-%s-%s' % (slug(lname), (i + 1) // 2, j),
                            language_map[lname],
                            lname.replace('_', ' '),
                            concepticon[concept],
                            concept,
                            form,
                            ' '.join(clean_string(form)),
                            SOURCE
                        ])
        # three methods: turchin, sca, lexstat, turchin is fast (needs not threshold)
        cognates = iter_cognates(
            ds, column='Segments', method='turchin', threshold=0.55)

        # two methods for alignments: progressive or library
        dataset.cognates.extend(iter_alignments(
            ds, cognates, column='Segments', method='progressive'))

    dataset.write_cognates()
