# coding: utf8
from __future__ import unicode_literals, print_function, division

from pylexibank.util import download_and_unpack_zipfiles


URL = "http://www.quanthistling.info/data/downloads/csv/data.zip"


def download(dataset, *names):
    download_and_unpack_zipfiles(URL, dataset, *names)
