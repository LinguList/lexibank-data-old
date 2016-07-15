# coding: utf8
from __future__ import unicode_literals, print_function, division

from six.moves.urllib.request import urlretrieve
from clldutils.path import Path
from pycldf.util import Archive, MD_SUFFIX
from pycldf.dataset import Dataset


def url(id_, path='/', domain=None):
    return "http://{0}{1}".format(domain or '{0}.clld.org'.format(id_), path)


def download(dataset, id_, domain=None):
    url_ = url(
        id_, domain=domain, path="/static/download/{0}-dataset.cldf.zip".format(id_))
    urlretrieve(url_, dataset.raw.joinpath('{0}.zip'.format(id_)).as_posix())


def itercldf(dataset, id_):
    archive = Archive(dataset.raw.joinpath('{0}.zip'.format(id_)))
    for name in archive.namelist():
        if name.endswith(MD_SUFFIX):
            yield Dataset.from_metadata(Path(name), archive)
