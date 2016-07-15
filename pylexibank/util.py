from __future__ import unicode_literals
import sys
import logging
import re
from contextlib import contextmanager
from tempfile import mkdtemp

import xlrd
from clldutils.dsv import reader, UnicodeWriter
from clldutils.path import Path, as_posix, rmtree
from clldutils.misc import slug
from pycldf.sources import Source, Reference

import pylexibank

logging.basicConfig(level=logging.INFO)
REPOS_PATH = Path(pylexibank.__file__).parent.parent
YEAR_PATTERN = re.compile('\s+\(?(?P<year>[1-9][0-9]{3}(\-[0-9]+)?)(\)|\.)')


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
