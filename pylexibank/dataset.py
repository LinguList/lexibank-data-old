# coding: utf8
from __future__ import unicode_literals, print_function, division
import logging
import re
from importlib import import_module
from collections import defaultdict, Counter

from clldutils import jsonlib
from clldutils.dsv import reader
from clldutils.misc import UnicodeMixin, cached_property
from pyglottolog.api import Glottolog
from pyconcepticon.api import Concepticon
from pycldf import csv
from pycldf.dataset import Dataset as CldfDatasetBase
from pycldf.dataset import MD_SUFFIX
from pycldf.metadata import Metadata as CldfMetadataBase
from tqdm import tqdm

import pylexibank
from pylexibank.util import with_sys_path, data_path, MarkdownTable
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


class Metadata(CldfMetadataBase):
    @property
    def notes(self):
        return {o['dc:title']: o.get('properties', {})
                for o in self.get_table().get('notes', [])}


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
        self.glottolog_languoids = {}

    @classmethod
    def from_name(cls, name):
        return cls(data_path(name))

    @cached_property()
    def glottocode_by_iso(self):
        return {l.iso_code: l.id for l in self.glottolog_languoids.values() if l.iso_code}

    def iter_cldf_metadata(self):
        for fname in sorted(self.cldf_dir.glob('*' + MD_SUFFIX), key=lambda f: f.name):
            yield Metadata.from_file(fname)

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
        self._run_command('cldf', Concepticon(kw.pop('concepticon_repos')), **kw)

    def download(self, **kw):
        self._run_command('download', **kw)

    def report(self, **kw):
        rep = TranscriptionReport(self, self.dir.joinpath('transcription.json'))
        res = rep.run(**getattr(self.commands, 'TRANSCRIPTION_REPORT_CFG', {}))
        if res:
            with self.dir.joinpath('TRANSCRIPTION.md').open('w', encoding='utf8') as fp:
                fp.write(res)


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
            general_errors=0,
            word_errors=0,
            bad_words=[],
            segment_types=Counter(),
        ))
        bad_words = []
        with tqdm(total=self.dataset.count_cldf_datasets, desc='cldf-ds', leave=False) as pbar:
            for ds in self.dataset.iter_cldf_datasets():
                bad_words.extend(test_sequences(ds, get_variety_id, self.report, **cfg))
                pbar.update(1)

        stats = dict(
            invalid=set(),
            tokens=0,
            segments=set(),
            lingpy_errors=set(),
            clpa_errors=set(),
            replacements=defaultdict(set),
            inventory_size=0,
            general_errors=0,
            word_errors=0,
            bad_words=[],
            segment_types=Counter(),
        )
        for lid, report in self.report.items():
            stats['invalid'].update(report['invalid'])
            stats['tokens'] += sum(report['segments'].values())
            stats['segments'].update(report['segments'].keys())
            
            for segment, count in report['segments'].items():
                stats['segment_types'][segment] += count

            stats['general_errors'] += report['general_errors']
            stats['word_errors'] += report['word_errors']
            stats['bad_words'] += report['bad_words']
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
        for attr in ['lingpy_errors', 'clpa_errors']:
            stats[attr+'_types'] = sorted(stats[attr])
        for attr in ['invalid', 'segments', 'lingpy_errors', 'clpa_errors']:
            stats[attr] = len(stats[attr])
        for segment in stats['replacements']:
            stats['replacements'][segment] = sorted(stats['replacements'][segment])

        self.report['stats'] = stats
        jsonlib.dump(self.report, self.fname, indent=4)

        if not cfg.get('segmentized'):
            return

        segments = MarkdownTable('Segment', 'Occurrence', 'LingPy', 'CLPA')
        for a, b in sorted(stats['segment_types'].items(), key=lambda x: (-x[1], x[0])):
            c, d = '✓', '✓'
            if a in stats['clpa_errors_types']:
                c = '✓' if a not in stats['lingpy_errors_types'] else '?'
                d = ', '.join(stats['clpa_errors_types'][a]) \
                    if a not in stats['clpa_errors_types'] else '?'
            segments.append([a, b, c, d])

        words = MarkdownTable('ID', 'LANGUAGE', 'CONCEPT', 'VALUE', 'SEGMENTS')
        with tqdm(total=len(bad_words), desc='bad-lexemes', leave=False) as pbar:
            for i, row in enumerate(bad_words):
                analyzed = []
                for segment in row[cfg['column']].split(' '):
                    if segment in stats['lingpy_errors_types'] \
                            or segment in stats['clpa_errors_types']:
                        analyzed.append('<s> %s </s>' % segment)
                    else:
                        analyzed.append(segment)
                words.append([
                    row['ID'],
                    row['Language_name'],
                    row['Parameter_name'],
                    row['Value'],
                    ' '.join(analyzed)])
                if i % 10 == 0:
                    pbar.update(10)
        return """\
# Detailed transcription record

## Segments

{0}
## Words

{1}""".format(segments.render(), words.render())

    def __unicode__(self):
        md = """## Transcription Report
### General Statistics
* Number of Tokens: {tokens}
* Number of Segments: {segments}
* Invalid forms: {invalid}
* Inventory Size: {inventory_size:.2f}
* [Erroneous tokens](report.md#tokens): {general_errors}
""".format(**self.report['stats'])

        md += """\
* Erroneous words: {0}
* Number of LingPy-Errors: {1}
* Number of CLPA-Errors: {2}
* Bad words: {3}
""".format(
            self.report['stats']['word_errors'], 
            self.report['stats']['lingpy_errors'],
            self.report['stats']['clpa_errors'],
            len(self.report['stats']['bad_words']),
        )

        return md


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
        macroareas = set()
        for row in self.rows:
            if row['Language_ID'] in self.dataset.glottolog_languoids:
                for ma in self.dataset.glottolog_languoids[row['Language_ID']].macroareas:
                    macroareas.add(ma)
        stats = {
            'dc:title': 'stats',
            'properties': {
                'lexeme_count': len(self.rows),
                'macroareas': list(macroareas),
            }
        }
        if 'notes' in self.table:
            self.table['notes'].append(stats)
        else:
            self.table['notes'] = [stats]
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
