# coding=utf-8
from __future__ import unicode_literals, print_function

from clldutils.misc import slug
from clldutils.dsv import UnicodeReader

from pylexibank.dataset import CldfDataset
from pylexibank.lingpy_util import getEvoBibAsSource


SOURCE = 'Wang2004'


def download(dataset, **kw):
    pass


def cldf(dataset, concepticon, **kw):
    with UnicodeReader(dataset.raw.joinpath('Wang2004.csv'), delimiter='\t') as reader:
        lines = list(reader)
    lmap = dict([(x['ABBREVIATION'], (x['GLOTTOCODE'], x['ISO'], x['NAME'])) for x in
        dataset.languages])
    cmap = {c.english: c.concepticon_id for c in dataset.conceptlist.concepts.values()}

    with CldfDataset((
        'ID',
        'Language_ID',
        'Language_name',
        'Language_iso',
        'Parameter_ID',
        'Parameter_name',
        'Value',
        'Source',
        'Cognacy',
        )
            , dataset) as ds:
        ds.sources.add(getEvoBibAsSource(SOURCE))
        idx = 1
        cogids = {0: 0}
        for i, line in enumerate(lines[1:]):
            concept = line[0]
            cid = cmap[concept]

            for t, cogs in zip(lines[0][1:], line[1:]):
                glottocode, iso, taxon = lmap[t]
                for cog in cogs.split('/'):
                    if cog in cogids:
                        cogid = cogids[cog]
                    else:
                        cogid = max(list(cogids.values()) or 0) + 1
                        cogids[cog] = cogid
                    ds.add_row((
                        idx, glottocode, taxon, iso, cid, concept, cog, SOURCE,
                        cogid))
                    dataset.cognates.append([
                        idx,
                        ds.name,
                        cog,
                        '-'.join([slug(concept), str(cogid)]),
                        '',
                        'expert',
                        SOURCE,
                        '', '', ''])
                    idx += 1
