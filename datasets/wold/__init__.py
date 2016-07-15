# coding: utf8
from __future__ import unicode_literals, print_function, division

from pylexibank.providers import clld
from pylexibank.dataset import CldfDataset


def download(dataset, **kw):
    clld.download(dataset, __name__)


def cldf(dataset, glottolog, concepticon, **kw):
    unmapped = set()
    for ods in clld.itercldf(dataset, __name__):
        lid = ods.name.split('-')[-1]
        fields = list(ods.fields) + ['Language_local_ID', 'Parameter_local_ID', 'Loan']
        with CldfDataset(fields, dataset, subset=lid) as ds:
            ds.table.schema.columns['Loan'].datatype = 'boolean'
            ds.table.schema.columns['Parameter_local_ID'].valueUrl = \
                clld.url(__name__, path='/meaning/{Parameter_local_ID}')
            ds.table.schema.columns['Language_local_ID'].valueUrl = \
                clld.url(__name__, path='/language/{Language_local_ID}')
            ds.table.schema.columns['Word_ID'].valueUrl = \
                clld.url(__name__, path='/word/{Word_ID}')
            ds.metadata.update(
                {k: v for k, v in ods.metadata.items() if k.startswith('dc:')})
            ds.sources.add(*ods.sources.items())
            for row in ods.rows:
                if row['Language_ID'] == 'None':
                    row['Language_ID'] = None
                    unmapped.add((row['Language_name'], lid))
                # Note: We count words marked as "probably borrowed" as loans.
                row = row.to_list() + [
                    lid, row['WOLD_Meaning_ID'], float(row['Borrowed_score']) > 0.6]
                ds.add_row(row)
    assert not unmapped
