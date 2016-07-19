# coding: utf8
from __future__ import unicode_literals, print_function, division

from pylexibank.providers import clld
from pylexibank.dataset import CldfDataset
from pylexibank.util import split


def download(dataset, **kw):
    clld.download(dataset, __name__)


def cldf(dataset, glottolog, concepticon, **kw):
    unmapped = set()
    for ods in clld.itercldf(dataset, __name__):
        lid = ods.name.split('-')[-1]
        fields = list(ods.fields) + [
            'Language_local_ID', 'Parameter_local_ID', 'Loan', 'Context']
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
                keys = list(row.keys())
                for i, (form, context) in enumerate(split(row['Value'])):
                    _row = row.to_list()
                    _row[keys.index('Value')] = form
                    _row[keys.index('ID')] = '%s-%s' % (row['ID'], i + 1)
                    # Note: We count words marked as "probably borrowed" as loans.
                    _row.extend([
                        lid,
                        row['WOLD_Meaning_ID'],
                        float(row['Borrowed_score']) > 0.6,
                        context])
                    ds.add_row(_row)
    assert not unmapped
