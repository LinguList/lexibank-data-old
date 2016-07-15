# coding: utf8
from __future__ import unicode_literals, print_function, division

import requests
from bs4 import BeautifulSoup as bs
from clldutils import jsonlib

LIMIT = 1000
BASE_URL = "http://transnewguinea.org"


def get(dataset, resource, offset=0, limit=LIMIT, download_=False):
    fname = dataset.raw.joinpath("%(resource)s-%(limit)s-%(offset)s.json" % locals())
    if fname.exists() and not download_:
        return jsonlib.load(fname)
    if not download_:
        raise ValueError
    res = requests.get(
        "{0}/api/v1/{1}/".format(BASE_URL, resource),
        params=dict(format='json', limit='{0}'.format(limit), offset='{0}'.format(offset))
    ).json()
    jsonlib.dump(res, fname)
    return res


def get_concept_ids(dataset, download_=False):
    """

    :return:
    """
    ids = []
    for page in range(1, 5):
        fname = dataset.raw.joinpath('c%s.html' % page)
        if fname.exists() and not download_:
            with fname.open(encoding='utf8') as fp:
                html = fp.read()
        else:
            if not download_:
                raise ValueError
            html = requests.get(
                "{0}/word/?subset=swadesh-200&page={1}".format(BASE_URL, page)).text
            with fname.open('w', encoding='utf8') as fp:
                fp.write(html)

        for td in bs(html, 'html5lib').find_all('td', **{'class': 'id'}):
            ids.append(int(td.find('a').get_text()))
    return ids


def get_objects(dataset, resource, download_=False):
    items = []
    offset = 0
    res = get(dataset, resource, download_=download_)
    while res['objects']:
        items.extend(res['objects'])
        offset += LIMIT
        res = get(dataset, resource, offset=offset, download_=download_)
    return {i['resource_uri']: i for i in items}


def get_all(dataset, download_=False):
    res = {'concept_ids': get_concept_ids(dataset, download_=download_)}
    for rsc in ['language', 'source', 'word', 'lexicon']:
        res[rsc] = get_objects(dataset, rsc, download_=download_)
    return res
