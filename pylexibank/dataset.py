# coding: utf8
from __future__ import unicode_literals, print_function, division
import logging
import re
from importlib import import_module

from clldutils import jsonlib
from clldutils.dsv import reader
from pyglottolog.api import Glottolog
from pyconcepticon.api import Concepticon
from pycldf import csv
from pycldf.dataset import Dataset as CldfDatasetBase
from pycldf.dataset import MD_SUFFIX

import pylexibank
from pylexibank.util import with_sys_path

logging.basicConfig(level=logging.INFO)
REQUIRED_FIELDS = ('ID', 'Language_ID', 'Parameter_ID', 'Value')
GC_PATTERN = re.compile('[a-z][a-z0-9]{3}[1-9][0-9]{3}$')


class Dataset(object):
    def __init__(self, path):
        self.id = path.name
        self.log = logging.getLogger(pylexibank.__name__)
        self.dir = path
        self.raw = self.dir.joinpath('raw')
        if not self.raw.exists():
            self.raw.mkdir()
        self.cldf_dir = self.dir.joinpath('cldf')
        if not self.cldf_dir.exists():
            self.cldf_dir.mkdir()
        with with_sys_path(self.dir.parent):
            self.commands = import_module(self.id)
        self.md = jsonlib.load(self.dir.joinpath('metadata.json'))
        self.languages = []
        lpath = self.dir.joinpath('languages.csv')
        if lpath.exists():
            for item in reader(lpath, dicts=True):
                assert not item['GLOTTOCODE'] or GC_PATTERN.match(item['GLOTTOCODE'])
                self.languages.append(item)
        self.conceptlist = None
        url = self.md.get('dc:conformsTo')
        if url and url.startswith('http://concepticon.clld.org/contributions/'):
            self.conceptlist = url.split('/')[-1]
        self.concepts = []
        cpath = self.dir.joinpath('concepts.csv')
        if cpath.exists():
            self.concepts = list(reader(cpath, dicts=True))
        self.cognates = Cognates()
        self.alignments = Alignments()

    def iter_cldf_datasets(self):
        for fname in self.cldf_dir.glob('*' + MD_SUFFIX):
            yield CldfDatasetBase.from_metadata(fname)

    def write_cognates(self):
        self.cognates.write(self.cldf_dir)
    def write_alignments(self):
        self.alignments.write(self.cldf_dir)

    def cognate_stats(self):
        cognates = self.cognates.read(self.cldf_dir)
        return len(cognates), len(set(r['Cognate_set_ID'] for r in cognates))

    def _run_command(self, name, *args, **kw):
        if not hasattr(self.commands, name):
            self.log.warn('command "%s" not available for dataset %s' % (name, self.id))
        else:
            getattr(self.commands, name)(self, *args, **kw)

    def cldf(self, **kw):
        self._run_command(
            'cldf',
            Glottolog(kw.pop('glottolog_repos')),
            Concepticon(kw.pop('concepticon_repos')),
            **kw)

    def download(self, **kw):
        self._run_command('download', **kw)

    def report(self, **kw):
        self._run_command('report', **kw)


class Cognates(list):
    fields = ['Word_ID', 'Wordlist_ID', 'Form', 'Cognate_set_ID', 'doubt']
    table = {
        'url': 'cognates.csv',
        'tableSchema': {'columns': [{'name': n, 'datatype': 'string'} for n in fields]}
    }
    table['tableSchema']['columns'][0]['valueUrl'] = \
        '{Wordlist_ID}.csv#{Word_ID}'

    def write(self, container):
        with csv.Writer(self.table, container=container) as writer:
            writer.writerows(sorted(self, key=lambda r: (r[3], r[1], r[0])))

    def read(self, container):
        with csv.Reader(self.table, container=container) as reader:
            return list(reader)

class Alignments(list):
    fields = ['Word_ID', 'Wordlist_ID', 'Alignment', 'Cognate_set_ID', 'doubt']
    table = {
        'url': 'alignments.csv',
        'tableSchema': {'columns': [{'name': n, 'datatype': 'string'} for n in fields]}
    }
    table['tableSchema']['columns'][0]['valueUrl'] = \
        '{Wordlist_ID}.csv#{Word_ID}'

    def write(self, container):
        with csv.Writer(self.table, container=container) as writer:
            writer.writerows(sorted(self, key=lambda r: (r[3], r[1], r[0])))

    def read(self, container):
        with csv.Reader(self.table, container=container) as reader:
            return list(reader)

class CldfDataset(CldfDatasetBase):
    def __init__(self, fields, dataset, subset=None):
        super(CldfDataset, self).__init__(
            '%s-%s' % (dataset.id, subset) if subset else dataset.id)
        if not all(x in fields for x in REQUIRED_FIELDS):
            raise ValueError('required field is missing')
        self.fields = tuple(fields)
        self.dataset = dataset

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write(outdir=self.dataset.cldf_dir)

    def write(self, **kw):
        self.table.schema.columns['Parameter_ID'].valueUrl = \
            'http://concepticon.clld.org/parameters/{Parameter_ID}'
        self.table.schema.columns['Language_ID'].valueUrl = \
            'http://glottolog.org/resource/languoid/id/{Language_ID}'
        self.metadata['tables'].append(Cognates.table)
        #self.metadata['tables'].append(Alignments.table)
        super(CldfDataset, self).write(**kw)


class Unmapped(object):
    def __init__(self, sortkey=None):
        if sortkey is None:
            sortkey = lambda y: y
        self.sortkey = sortkey
        self.languages = set()
        self.concepts = set()

    def pprint(self):
        if self.languages:
            print('ID,NAME,ISO,GLOTTOCODE,GLOTTOLOG_NAME')
            for lang in sorted(self.languages, key=self.sortkey):
                print('%s,"%s",%s,,' % tuple(r or '' for r in lang))
            print('================================')
        if self.concepts:
            print('ID,GLOSS,CONCEPTICON_ID,CONCEPTICON_GLOSS')
            for c in sorted(self.concepts, key=self.sortkey):
                print('%s,"%s",,' % tuple(r or '' for r in c))
