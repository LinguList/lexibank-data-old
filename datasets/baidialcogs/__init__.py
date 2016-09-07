# coding=utf-8
from __future__ import unicode_literals, print_function

import lingpy as lp

from pylexibank.dataset import Dataset
from pylexibank.lingpy_util import iter_alignments, wordlist2cognates


def download(dataset):
    pass


def cldf(dataset, concepticon, **kw):
    orig_ds = Dataset.from_name('baidial')
    orig_ds.commands.cldf(dataset, concepticon, **kw)

    for cldfds in dataset.iter_cldf_datasets():
        for attr in ['dc:isVersionOf', 'dc:provenance']:
            cldfds.table[attr] = dataset.md[attr]
        cldfds.write(outdir=dataset.cldf_dir)

        # assuming that we don't need anything, I only load the wordlist, align it
        # in lingpy, and create cognates and alignments, currently, there is no
        # real source, so I'll just make a fake source "List2016i", but the dataset
        # should be published with zenodo, ideally
        alm = lp.Alignments(dataset.raw.joinpath('BDS-cognates.tsv').as_posix())

        cognates = wordlist2cognates(alm, cldfds, 'List2016i')
        dataset.cognates.extend(iter_alignments(alm, cognates))
