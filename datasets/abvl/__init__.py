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

PROVIDER = "Lees2013"
SOURCE = "Hattori1960"

def download(dataset):

    xls2csv(dataset.raw.joinpath('AinuHattoriChiri.xlsx'), outdir=dataset.raw)
