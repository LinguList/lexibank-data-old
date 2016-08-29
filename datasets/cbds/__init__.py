# coding=utf-8
from __future__ import unicode_literals, print_function

from six import text_type
from clldutils.misc import slug
from clldutils.path import Path
import lingpy as lp
from collections import namedtuple

from pylexibank.dataset import CldfDataset
from pylexibank.lingpy_util import (getEvoBibAsSource, iter_alignments,
        clean_string, wordlist2cognates)

def download(dataset):

    pass

def cldf(dataset, glottolog, concepticon, **kw):

    # assuming that we don't need anything, I only load the wordlist, align it
    # in lingpy, and create cognates and alignments, currently, there is no
    # real source, so I'll just make a fake source "List2016i", but the dataset
    # should be published with zenodo, ideally
    alm = lp.Alignments(dataset.raw.joinpath('BDS-cognates.tsv').as_posix())

    # don't know how to reference the name of the dataset other than with named
    # tuple
    ds = namedtuple('dataset', 'name')
    ds.name = 'cdbs'

    cognates = wordlist2cognates(alm, ds, 'List2016i')
    dataset.cognates.extend(iter_alignments(alm, cognates))
