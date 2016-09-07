# coding=utf-8
from __future__ import unicode_literals, print_function

from pylexibank.dataset import CldfDataset, REQUIRED_FIELDS


def download(dataset, **kw):
    raise NotImplemented


def cldf(dataset, concepticon, **kw):
    """
    Implements the conversion of the raw data to CLDF dataset(s).

    :param dataset: provides access to the information in supplementary files as follows:\
     - the JSON object from `metadata.json` is available as `dataset.md`\
     - items from languages.csv are available as `dataset.languages`\
     - items from concepts.csv are available as `dataset.concepts`\
     - if a Concepticon conceptlist was specified in metadata.json, its ID is available\
       as `dataset.conceptlist`
    :param concepticon:  a pyconcepticon.api.Concepticon` instance.
    :param kw: All arguments passed on the command line.

    .. notes::

        There's also a dict `dataset.glottolog_languoids` mapping Glottocodes to \
        Glottolog languoid objects.
    """
    with CldfDataset(REQUIRED_FIELDS, dataset) as ds:
        pass
