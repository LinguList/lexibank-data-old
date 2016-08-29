# coding: utf8
from __future__ import unicode_literals, print_function, division
import logging
import re
from importlib import import_module
from collections import defaultdict, Counter

from clldutils import jsonlib
from clldutils.dsv import reader
from clldutils.misc import UnicodeMixin
from pyglottolog.api import Glottolog
from pyconcepticon.api import Concepticon
from pycldf import csv
from pycldf.dataset import Dataset as CldfDatasetBase
from pycldf.dataset import MD_SUFFIX

import pylexibank
from pylexibank.util import with_sys_path, data_path
from pylexibank.lingpy_util import test_sequences

logging.basicConfig(level=logging.INFO)
REQUIRED_FIELDS = ('ID', 'Language_ID', 'Parameter_ID', 'Value')
GC_PATTERN = re.compile('[a-z][a-z0-9]{3}[1-9][0-9]{3}$')


def get_variety_id(row):
    lid = row.get('Language_local_ID')
    if not lid:
        lid = row.get('Language_name')
    if not lid:
        lid = row.get('Language_ID')
    return lid


def synonymy_index(cldfds):
    synonyms = defaultdict(Counter)
    for row in cldfds.rows:
        lid = get_variety_id(row)
        if lid and row['Parameter_ID']:
            synonyms[lid].update([row['Parameter_ID']])
    return (
        sum([sum(list(counts.values())) /
             float(len(counts)) for counts in synonyms.values()]),
        set(synonyms.keys()))


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

    @classmethod
    def from_name(cls, name):
        return cls(data_path(name))

    def iter_cldf_datasets(self):
        for fname in sorted(self.cldf_dir.glob('*' + MD_SUFFIX), key=lambda f: f.name):
            yield CldfDatasetBase.from_metadata(fname)

    def write_cognates(self):
        self.cognates.write(self.cldf_dir)

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
        rep = TranscriptionReport(self, self.dir.joinpath('transcription.json'))
        rep.run(**getattr(self.commands, 'TRANSCRIPTION_REPORT_CFG', {}))


class Cognates(list):
    fields = [
        'Word_ID',
        'Wordlist_ID',
        'Form',
        'Cognate_set_ID',
        'Doubt',
        'Cognate_detection_method',
        'Cognate_source',
        'Alignment',
        'Alignment_method',
        'Alignment_source',
    ]
    table = {
        'url': 'cognates.csv',
        'tableSchema': {'columns': [{'name': n, 'datatype': 'string'} for n in fields]}
    }
    table['tableSchema']['columns'][0]['valueUrl'] = '{Wordlist_ID}.csv#{Word_ID}'

    def write(self, container):
        cognatesets = Counter(r[3] for r in self)
        with csv.Writer(self.table, container=container) as writer:
            for row in sorted(self, key=lambda r: (r[3], r[1], r[0])):
                if cognatesets[row[3]] > 1:
                    row = list(row)
                    if isinstance(row[7], list):
                        row[7] = ' '.join(row[7])
                    writer.writerow(row)

    def read(self, container):
        with csv.Reader(self.table, container=container) as reader:
            return list(reader)


def valid_Value(row):
    return bool(row['Value']) and row['Value'] not in ['?', '-']


VALIDATORS = {
    'Value': valid_Value,
}


class TranscriptionReport(UnicodeMixin):
    def __init__(self, dataset, fname):
        self.dataset = dataset
        self.fname = fname
        if fname.exists():
            try:
                self.report = jsonlib.load(fname)
            except ValueError:
                self.report = {}
        else:
            self.report = {}

    def run(self, **cfg):
        cfg.setdefault('column', 'Value')
        cfg.setdefault('segmentized', False)
        self.report = defaultdict(lambda: dict(
            invalid=Counter(),
            segments=Counter(),
            lingpy_errors=set(),
            clpa_errors=set(),
            replacements=defaultdict(set),
        ))
        for ds in self.dataset.iter_cldf_datasets():
            test_sequences(ds, get_variety_id, self.report, **cfg)

        stats = dict(
            invalid=set(),
            tokens=0,
            segments=set(),
            lingpy_errors=set(),
            clpa_errors=set(),
            replacements=defaultdict(set),
            inventory_size=0)
        for lid, report in self.report.items():
            stats['invalid'].update(report['invalid'])
            stats['tokens'] += sum(report['segments'].values())
            stats['segments'].update(report['segments'].keys())
            for attr in ['lingpy_errors', 'clpa_errors']:
                stats[attr].update(report[attr])
            for segment, repls in report['replacements'].items():
                stats['replacements'][segment].update(repls)
            stats['inventory_size'] += len(report['segments']) / len(self.report)
            # make sure we can serialize as JSON:
            for attr in ['lingpy_errors', 'clpa_errors']:
                report[attr] = sorted(report[attr])
            for segment in report['replacements']:
                report['replacements'][segment] = sorted(report['replacements'][segment])
        # make sure we can serialize as JSON:
        for attr in ['invalid', 'segments', 'lingpy_errors', 'clpa_errors']:
            stats[attr] = len(stats[attr])
        for segment in stats['replacements']:
            stats['replacements'][segment] = sorted(stats['replacements'][segment])

        self.report['stats'] = stats
        jsonlib.dump(self.report, self.fname, indent=4)

    def __unicode__(self):
        md = """## Transcription Report
### General Statistics
* Number of Tokens: {number_of_tokens}
* Number of Segments: {number_of_segments}
* Invalid forms: {invalid_rows}
* Inventory Size: {inventory_size:.2f}
""".format(**self.report['stats'])

        md += """\
* Number of Errors: {0}
* Number of LingPy-Errors: {1}
* Number of CLPA-Errors: {2}
""".format(
            0,  # FIXME
            self.report['stats']['number_of_errors']['lingpy'],
            self.report['stats']['number_of_errors']['clpa'],
        )

        """
{modified}
## Detailed listing of recognized segments
{segments}
"""

        return md

        segments = '| Segment | Occurrence | LingPy | CLPA | \n|---|---|---|---|\n'
        for a, b in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            if a in errors:
                c = '✓' if 'lingpy' not in errors[a] else '?'
                d = ', '.join(errors[a]) if 'clpa' not in errors[a] else '?'
            else:
                c, d = '✓', '✓'
            segments += '| {0} | {1} | {2} | {3} |\n'.format(a, b, c, d)

        return text.format(
            dataset=dataset.name,
            NOT=number_of_tokens,
            NOS=number_of_segments,
            NOE=number_of_errors,
            NOL=number_of_lingpy_errors,
            NOC=number_of_clpa_errors,
            IVS=inventory_size,
            modified='\n## Automatically modified (CLPA)\n' +
                     '| Source | Target |\n|---|---|\n' +
                     ''.join(['| {0} | {1} |\n'.format(a, b) for a, b in modified])
            if modified else '',
            segments=segments)


class CldfDataset(CldfDatasetBase):
    def __init__(self, fields, dataset, subset=None):
        super(CldfDataset, self).__init__(
            '%s-%s' % (dataset.id, subset) if subset else dataset.id)
        if not all(x in fields for x in REQUIRED_FIELDS):
            raise ValueError('required field is missing')
        self.fields = tuple(fields)
        self.dataset = dataset
        self.validators = {k: v for k, v in VALIDATORS.items()}
        for name in dir(self.dataset.commands):
            if name.startswith('valid_'):
                if callable(getattr(self.dataset.commands, name)):
                    self.validators[name.split('_', 1)[1]] = getattr(
                        self.dataset.commands, name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write(outdir=self.dataset.cldf_dir)

    def add_row(self, row):
        #
        # add segments column, value cleaned from "<>=..."
        #
        row = CldfDatasetBase.add_row(self, row)
        if row:
            for col, validator in self.validators.items():
                if not validator(row):
                    del self._rows[row['ID']]
                    return
        return row

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
