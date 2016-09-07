# coding=utf8
from __future__ import unicode_literals
import sys
import logging
import re
from contextlib import contextmanager
from tempfile import mkdtemp
import zipfile
from tabulate import tabulate

from six.moves.urllib.request import urlretrieve
import xlrd
from clldutils.dsv import reader, UnicodeWriter
from clldutils.path import Path, as_posix, rmtree, copy
from clldutils.misc import slug
from pycldf.sources import Source, Reference

import pylexibank

logging.basicConfig(level=logging.INFO)
REPOS_PATH = Path(pylexibank.__file__).parent.parent
YEAR_PATTERN = re.compile('\s+\(?(?P<year>[1-9][0-9]{3}(-[0-9]+)?)(\)|\.)')


class MarkdownTable(list):
    def __init__(self, *cols):
        self.columns = list(cols)
        list.__init__(self)

    @staticmethod
    def tr(row):
        return '|'.join(['%s' % c for c in row])

    def render(self, fmt='pipe', sortkey=None, condensed=True):
        res = tabulate(sorted(self, key=sortkey) if sortkey else self, self.columns, fmt)
        if condensed:
            res = re.sub('[ ]+', ' ', res)
        if fmt == 'pipe':
            res += '\n\n(%s rows)\n\n' % len(self)
        return res


def clean_form(form):
    form = form.replace('(?)', '').strip()
    if form.startswith('['):
        if form.endswith(']'):
            form = form[1:-1].strip()
        elif ']' not in form[1:]:
            form = form[1:].strip()
    if form.startswith('('):
        if form.endswith(')'):
            form = form[1:-1].strip()
        elif ']' not in form[1:]:
            form = form[1:].strip()
    return form


def split(s, sep=',;', exclude_contexts=None):
    exclude_contexts = dict(exclude_contexts or [('[', ']'), ('(', ')'), ('“', '”')])
    token, context = '', ''
    in_context = []
    ignore_sep = False
    for c in s:
        if c in exclude_contexts:
            ignore_sep = True
            if token and token[-1] == ' ':
                in_context.append(exclude_contexts[c])

        if c in sep and not in_context and not ignore_sep:
            if token.strip():
                yield token.strip(), context.strip() or None
                token, context = '', ''
        else:
            if in_context:
                context += c
            else:
                token += c

        if c in exclude_contexts.values():
            ignore_sep = False
            if in_context and c == in_context[-1]:
                in_context.pop()
                if not in_context:
                    context += ' '

    if token.strip():
        yield token.strip(), context.strip() or None


def formatted_number(n):
    if isinstance(n, set):
        n = len(n)
    s = '%s' % n
    sr = list(reversed(s))
    return ''.join(reversed(
        ','.join([''.join(sr[i:i + 3]) for i in range(0, len(sr), 3)])))


@contextmanager
def with_temp_dir():
    tmpdir = Path(mkdtemp())
    yield tmpdir
    rmtree(tmpdir)


def xls2csv(fname, outdir=None):
    res = {}
    outdir = outdir or fname.parent
    wb = xlrd.open_workbook(as_posix(fname))
    for sname in wb.sheet_names():
        sheet = wb.sheet_by_name(sname)
        if sheet.nrows:
            path = outdir.joinpath(
                fname.stem + '.' + slug(sname, lowercase=False) + '.csv')
            with UnicodeWriter(path) as writer:
                for i in range(sheet.nrows):
                    writer.writerow([col.value for col in sheet.row(i)])
            res[sname] = path
    return res


def split_by_year(s):
    match = YEAR_PATTERN.search(s)
    if match:
        return s[:match.start()].strip(), match.group('year'), s[match.end():].strip()
    return None, None, s


def get_reference(author, year, title, pages, sources, id_=None, genre='misc'):
    kw = {'title': title}
    id_ = id_ or None
    if author and year:
        id_ = id_ or slug(author + year)
        kw.update(author=author, year=year)
    elif title:
        id_ = id_ or slug(title)

    if not id_:
        return

    source = sources.get(id_)
    if source is None:
        sources[id_] = source = Source(genre, id_, **kw)

    return Reference(source, pages)


def read_csv(path):
    return list(reader(path, dicts=True))


def data_path(*comps, **kw):
    return kw.get('repos', REPOS_PATH).joinpath('datasets', *comps)


@contextmanager
def with_sys_path(d):
    p = d.as_posix()
    sys.path.append(p)
    yield
    if sys.path[-1] == p:
        sys.path.pop()


def download_and_unpack_zipfiles(url, dataset, *paths):
    """Download zipfiles and immediately unpack the content"""
    with with_temp_dir() as tmpdir:
        urlretrieve(url, tmpdir.joinpath('ds.zip').as_posix())
        with zipfile.ZipFile(tmpdir.joinpath('ds.zip').as_posix()) as zipf:
            for path in paths:
                zipf.extract(as_posix(path), path=tmpdir.as_posix())
                copy(tmpdir.joinpath(path), dataset.raw)
