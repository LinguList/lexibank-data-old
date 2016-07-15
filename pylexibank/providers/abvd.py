# coding: utf8
from __future__ import unicode_literals, print_function, division
from xml.etree import cElementTree as et
import re

from six import text_type
import requests
from clldutils.misc import xmlchars, slug
from pycldf.sources import Source

from pylexibank.dataset import CldfDataset

URL = "http://language.psy.auckland.ac.nz/utils/save/?type=xml&section=%s&language=%d"
INVALID_LANGUAGE_IDS = {
    'austronesian': [261],  # Duplicate West Futuna list
}


def get_data(dataset, section, lid):
    req = requests.get(URL % (section, lid))
    if len(req.content) == 0:
        return None

    with dataset.raw.joinpath('%s.xml' % (lid)).open('w', encoding='utf8') as fp:
        fp.write(req.text)
    return True


def download(dataset, section):
    assert section in ['austronesian', 'bantu', 'mayan', 'utoaztecan']
    dataset.log.info(section)
    language_ids = [
        i for i in range(1, 1500) if i not in INVALID_LANGUAGE_IDS.get(section, [])]

    for language_id in language_ids:
        if not get_data(dataset, section, language_id):
            dataset.log.warn("No content for %s %d. Ending." % (section, language_id))
            break


def read_xml(path):
    with path.open(encoding='utf8') as fp:
        return et.fromstring(xmlchars('<r>%s</r>' % fp.read()).encode('utf8'))


class XmlElement(object):
    __attr_map__ = []

    def __init__(self, e):
        self.id = '%s' % int(e.find('id').text)
        self.e = e
        for spec in self.__attr_map__:
            if len(spec) == 2:
                attr, nattr = spec
                conv = None
            elif len(spec) == 3:
                attr, nattr, conv = spec
            else:
                raise ValueError(spec)
            nattr = nattr or attr
            ee = e.find(attr)
            if ee is not None:
                text = e.find(attr).text
                if text and not isinstance(text, unicode):
                    text = text.decode('utf8')
            else:
                text = ''
            if text:
                text = text.strip()

            if text and conv:
                text = conv(text)

            setattr(self, nattr, text or None)


class Language(XmlElement):
    __attr_map__ = [
        ('author', ''),
        ('language', 'name'),
        ('silcode', 'iso'),
        ('notes', ''),
        ('problems', ''),
        ('classification', ''),
        ('typedby', ''),
        ('checkedby', ''),
    ]

    def __init__(self, e):
        XmlElement.__init__(self, e)
        self.glottocode = None


class Entry(XmlElement):
    __attr_map__ = [
        ('word_id', '', lambda s: '%s' % int(s)),
        ('word', ''),
        ('item', 'name'),
        ('annotation', 'comment'),
        ('loan', ''),
        ('cognacy', ''),
        #('pmpcognacy', ''),
    ]

    def __init__(self, e, section):
        self.section = section
        XmlElement.__init__(self, e)

    @property
    def concept_id(self):
        return '%s-%s' % (self.section, int(self.word_id))

    @property
    def concept(self):
        return '%s [%s]' % (self.word, self.section)

    @property
    def cognates(self):
        res = set()
        for comp in re.split(',|/', self.cognacy or ''):
            comp = comp.strip().lower()
            if comp:
                doubt = False
                if comp.endswith('?'):
                    doubt = True
                    comp = comp[:-1].strip()
                res.add(('%s-%s' % (self.word_id, comp), doubt))
        return res


class Wordlist(object):
    def __init__(self, dataset, path, section):
        self.dataset = dataset
        e = read_xml(path)
        self.section = section
        records = list(e.findall('./record'))
        self.language = Language(records[0])
        self.entries = [Entry(r, section) for r in records[1:] if self.is_entry(r)]

    @staticmethod
    def is_entry(r):
        return getattr(r.find('id'), 'text', None) \
            and getattr(r.find('item'), 'text', None)

    def url(self, path):
        return 'http://language.psy.auckland.ac.nz/%s/%s' % (self.section, path)

    @property
    def name(self):
        return '%s - %s - %s' % (self.section, self.language.name, self.id)

    @property
    def id(self):
        return '%s-%s' % (self.section, self.language.id)

    def md(self):
        return dict(properties={
            k: getattr(self.language, k, None)
            for k in 'id name author notes problems typedby checkedby'.split()})

    def to_cldf(self, concept_map, unmapped, citekey=None, source=None, concept_key=None):
        if concept_key is None:
            concept_key = lambda entry: entry.word_id

        if not self.language.glottocode:
            unmapped.languages.add(
                (self.language.id, self.language.name, self.language.iso))

        with CldfDataset((
                'ID',
                'Language_ID',
                'Language_iso',
                'Language_name',
                'Language_local_ID',
                'Parameter_ID',
                'Parameter_name',
                'Parameter_local_ID',
                'Value',
                'Source',
                'Cognate_Set',
                'Comment',
                'Loan',
                ),
                self.dataset,
                subset=self.language.id) as ds:
            ds.metadata['dc:creator'] = self.language.author
            ds.metadata['dc:identifier'] = self.url('language.php?id=%s' % self.language.id)
            if self.language.typedby:
                ds.metadata['dc:contributor'] = self.language.typedby
            if self.language.checkedby:
                ds.metadata['dc:contributor'] = self.language.checkedby
            if self.language.notes:
                ds.metadata['dc:description'] = self.language.notes

            ds.table.schema.aboutUrl = '%s.csv#{ID}' % ds.name
            ds.table.schema.columns['Loan'].datatype = 'boolean'
            ds.table.schema.columns['Parameter_local_ID'].valueUrl = \
                self.url('word.php?v=1{Parameter_local_ID}')
            ds.table.schema.columns['Language_local_ID'].valueUrl = \
                self.url('language.php?id={Language_local_ID}')

            ref = None
            if citekey and source:
                ref = citekey
                ds.sources.add(Source('misc', citekey, title=source))

            for entry in self.entries:
                if entry.name == '?':
                    continue
                if not (citekey and source):
                    src = entry.e.find('source')
                    if src and getattr(src, 'text'):
                        ref = slug(text_type(src.text))
                        ds.sources.add(Source('misc', ref, title=src.text))
                cid = concept_map.get(concept_key(entry))
                if not cid:
                    unmapped.concepts.add((entry.word_id, entry.word))
                ds.add_row([
                    entry.id,
                    self.language.glottocode,
                    self.language.iso,
                    self.language.name,
                    self.language.id,
                    cid,
                    entry.word,
                    entry.word_id,
                    entry.name,
                    ref,
                    entry.cognacy,
                    entry.comment or '',
                    entry.loan == 'L',
                ])

    def cognates(self):
        for entry in self.entries:
            for cognate_set_id, doubt in entry.cognates:
                yield (
                    '%s-%s' % (self.section, entry.id),
                    self.id,
                    entry.name,
                    '%s-%s' % (self.section, cognate_set_id),
                    doubt)
