# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.dsv import UnicodeReader
from clldutils.misc import slug

from pylexibank.util import xls2csv
from pylexibank.lingpy_util import iter_alignments, segmentize
from pylexibank.dataset import CldfDataset


def download(dataset):
    xls2csv(dataset.raw.joinpath('supplementary.xlsx'), outdir=dataset.raw)
    xls2csv(dataset.raw.joinpath('Japonic_recovered.xlsx'), outdir=dataset.raw)


def read_csv(dataset, name, offset):
    header, rows = None, []
    with UnicodeReader(dataset.raw.joinpath(name)) as reader:
        for i, row in enumerate(reader):
            row = [c.strip() for c in row]
            if i == offset:
                header = row
            if i > offset:
                rows.append(row)
    return header, rows


def cldf(dataset, concepticon, **kw):
    language_map = {l['NAME']: l['GLOTTOCODE'] or None for l in dataset.languages}
    concept_map = {c['ENGLISH']: c['CONCEPTICON_ID']
                   for c in concepticon.conceptlist(dataset.conceptlist)}

    wordsh, words = read_csv(dataset, 'supplementary.Sheet1.csv', 0)
    cognatesh, cognates = read_csv(dataset, 'Japonic_recovered.Sheet1.csv', 1)

    def concepts(h, step):
        l = h[2:]
        return {i + 2: l[i] for i in range(0, len(l), step)}

    word_index_to_concept = concepts(wordsh, 1)

    assert all(c in concept_map for c in word_index_to_concept.values())
    assert len(words) == len(cognates)

    def sorted_(l):
        return sorted(l, key=lambda r: r[:2])

    cognatesets = []
    with CldfDataset((
            'ID',
            'Language_ID',
            'Language_name',
            'Parameter_ID',
            'Parameter_name',
            'Value',
            'Segments',
            'AltTranscription',
            ), dataset) as ds:
        for i, (word, cognate) in enumerate(zip(sorted_(words), sorted_(cognates))):
            if not word[1]:
                continue
            if word[1] == 'Nigata':
                word[1] = 'Niigata'
            assert word[:2] == cognate[:2]

            lname = word[1]
            lid = slug(lname)

            for index, concept in word_index_to_concept.items():
                if word[index] == '?':
                    continue
                wid = '%s-%s' % (lid, index - 1)
                cindex = (index - 1) * 2
                assert cognatesh[cindex] == concept
                ds.add_row([
                    wid,
                    language_map[lname],
                    lname,
                    concept_map[concept],
                    concept,
                    word[index],
                    '',
                    cognate[cindex],
                ])
                cs = cognate[cindex + 1]
                for css in cs.split('&'):
                    css = css.strip()
                    if css != '?':
                        css = int(float(css))
                        cognatesets.append([
                            wid,
                            ds.name,
                            word[index],
                            '%s-%s' % (index - 1, css),
                            False,
                            'expert',
                            '',
                            '',
                            '',
                            '',
                        ])
        segmentize(ds)
    dataset.cognates.extend(iter_alignments(ds, cognatesets, column='Segments'))
