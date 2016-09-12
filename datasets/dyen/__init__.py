# coding=utf-8
from __future__ import unicode_literals, print_function
import re
from collections import defaultdict, Counter

from pylexibank.dataset import CldfDataset

HEADER = re.compile('a (?P<number>[0-9]{3}) (?P<label>.+)')
SUBHEADER = re.compile('b\s+(?P<ccn>[0-9]+)$')
RELATION = re.compile('c\s+(?P<ccn1>[0-9]+)\s+(?P<relation>2|3)\s+(?P<ccn2>[0-9]+)$')
FORM = re.compile(
    '\s+(?P<mn>[0-9]{3})\s+(?P<ln>[0-9]{2})\s+(?P<variety>.{15})\s+(?P<forms>.*)')
MISSING_FORM = re.compile(
    '\s+(?P<mn>[0-9]{3})\s+(?P<ln>[0-9]{2})\s+(?P<variety>.{1,15})$')
VARIETY = re.compile('.{16} (?P<num>[0-9]{2}) (?P<name>.{15}) (?P<onum>[0-9]{2}) (?P<oname>.{15}) (?P<count>[0-9]{3})')


def download(dataset, **kw):
    return


def blocks(lines, pattern):
    md, block = None, []
    for line in lines:
        match = pattern.match(line)
        if match:
            if md:
                yield md, block
            md, block = match.groupdict(), []
        elif md:
            block.append(line)
    if md:
        yield md, block


def relations_and_forms(lines):
    rels, forms, missing = [], [], []
    for line in lines:
        if not line.strip():
            missing.append(line)
            continue
        match = RELATION.match(line)
        if match:
            rels.append(
                (match.group('ccn1'), match.group('relation'), match.group('ccn2')))
        else:
            match = FORM.match(line)
            if match:
                d = match.groupdict()
                forms.append((d['mn'], d['ln'], d['variety'].strip(), d['forms'].strip()))
            else:
                assert MISSING_FORM.match(line)
                missing.append(line)
    return rels, forms, missing


def parse(dataset):
    lines, in_data, varieties, meanings = [], False, {}, {}
    with dataset.raw.joinpath('iedata-with-intro.txt').open(encoding='utf8') as fp:
        for line in fp.read().split('\n'):
            if in_data:
                lines.append(line)
            else:
                match = VARIETY.match(line)
                if match:
                    varieties[match.group('num')] = match.groupdict()
            if line == '5. THE DATA':
                in_data = True

    meanings_per_variety = Counter()
    rels, forms = defaultdict(set), defaultdict(lambda: defaultdict(list))
    for md, block in blocks(lines, HEADER):
        mn = md['number']
        meanings[mn] = md['label']
        for md, subblock in blocks(block, SUBHEADER):
            r, f, m = relations_and_forms(subblock)
            assert len(r) + len(f) + len(m) == len(subblock)
            for rr in r:
                rels[mn].add(rr)
            for _, ln, variety, forms_ in f:
                assert _ == mn and ln in varieties
                meanings_per_variety.update([ln])
                if md['ccn'] != '000':  # discard inappropriate forms.
                    forms[mn][md['ccn']].append((ln, forms_))
    for mn, rels_ in rels.items():
        for s, _, t in rels_:
            assert int(s) >= 200 and int(t) >= 200 and s in forms[mn] and t in forms[mn]

    assert all(n == int(varieties[ln]['count']) for ln, n in meanings_per_variety.items())
    return varieties, meanings, forms, rels


def cldf(dataset, concepticon, **kw):
    concepticon = {
        c['NUMBER']: c['CONCEPTICON_ID']
        for c in concepticon.conceptlist(dataset.conceptlist)}
    varieties, meanings, allforms, rels = parse(dataset)

    with CldfDataset((
            'ID',
            'Language_ID',
            'Language_name',
            'Language_local_ID',
            'Parameter_ID',
            'Parameter_name',
            'Parameter_local_ID',
            'Value',
            'Cognate_class'), dataset) as ds:
        for mn, cognatesets in allforms.items():
            for ccn, forms in cognatesets.items():
                for ln, form in forms:
                    ffs = [ff.strip().lower() for ff in form.split(',')]
                    for i, f in enumerate(ffs):
                        wid = '%s-%s-%s' % (ln, mn, i + 1)
                        ds.add_row([
                            wid,
                            '',
                            varieties[ln]['name'].strip(),
                            ln,
                            concepticon[mn],
                            meanings[mn],
                            mn,
                            f,
                            '%s-%s' % (mn, ccn),
                        ])
                        if len(ffs) == 1 and (2 <= int(ccn) <= 99 or 200 <= int(ccn) <= 399):
                            # most conservative cognacy judgements only
                            dataset.cognates.append([
                                wid,
                                ds.name,
                                f,
                                '%s-%s' % (mn, ccn),
                                False,
                                'expert',
                                '',
                                '',
                                '',
                                '',
                            ])
