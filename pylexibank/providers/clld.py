# coding: utf8
from __future__ import unicode_literals, print_function, division

from six.moves.urllib.request import urlretrieve
from clldutils.path import Path
from pycldf.util import Archive, MD_SUFFIX
from pycldf.dataset import Dataset


def download(dataset, id_, domain=None):
    domain = domain or '{0}.clld.org'.format(id_)
    url = "http://{0}/static/download/{1}-dataset.cldf.zip".format(domain, id_)
    urlretrieve(url, dataset.raw.joinpath('{0}.zip'.format(id_)).as_posix())


def itercldf(dataset, id_):
    archive = Archive(dataset.raw.joinpath('{0}.zip'.format(id_)))
    for name in archive.namelist():
        if name.endswith(MD_SUFFIX):
            yield Dataset.from_metadata(Path(name), archive)
