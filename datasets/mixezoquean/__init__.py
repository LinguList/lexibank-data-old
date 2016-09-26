# coding=utf-8
from __future__ import unicode_literals, print_function
import re

from pylexibank.dataset import CldfDataset, TranscriptionReport
from clldutils.misc import slug
from clldutils.path import Path
from clldutils.dsv import UnicodeReader

from pylexibank.lingpy_util import getEvoBibAsSource, iter_alignments
from pylexibank.util import download_and_unpack_zipfiles
import lingpy as lp

PROVIDER = 'Cysouw2006a'
TRANSCRIPTION_REPORT_CFG = {'column': 'Segments', 'segmentized': True}
CONVERSION = {
        "š" : "ʃ",
        "-" : "+",
        "č" : "tʃ",
        "ïï" : "ɨː",
        "ï" : "ɨ",
        "ii" : "iː",
        "pp" : "pː",
        "tsts" : "tsː",
        "ææ" : "æː",
        "υυ" : "ʋː",
        "υ" : "ʋ",
        "kk" : "kː",
        "hs" : "h s",
        "Y" : "j",
        "y" : "j",
        "ε" : "ɛ",
        "ʔs" : "ʔ s"
        
        }
PREPARSE = [("-", "+")]

def download(dataset, **kw):
    pass

def cldf(dataset, concepticon, **kw):
    
    abb2lang = dict([(l['ABBREVIATION'], (l['GLOTTOCODE'], l['NAME'],
        l['SOURCE'])) for l in
        dataset.languages])
    concept_map = {c['ENGLISH']: c['CONCEPTICON_ID']
                   for c in concepticon.conceptlist(dataset.conceptlist)}    

    visited_sources = []
    cognates = []
    idx = 1
    cogidx = 1
    with UnicodeReader(dataset.raw.joinpath('Wordlist.txt'), delimiter='\t') as reader1,\
            UnicodeReader(dataset.raw.joinpath('Cognates.txt'), delimiter='\t') as reader2, \
            CldfDataset((
                'ID',
                'Language_ID',
                'Language_name',
                'Language_iso',
                'Parameter_ID',
                'Parameter_name',
                'Value',
                'Source',
                'Segments',
                'Cognacy'
                ), dataset) as ds:
        for i, (row1, row2) in enumerate(zip(reader1, reader2)):
            row = [c.strip() for c in row1]
            if i == 0:
                header = row1[1:]
            else:
                concept = re.split(' [-—–]', row1[0])[0]
                cid = concept_map[concept]
                for (abb, word, cog) in zip(header, row1[1:], row2[1:]):
                    if word.strip() and word.strip() != '?':
                        segments = lp.sequence.sound_classes.clean_string(word,
                                splitters='~,', rules=CONVERSION,
                                preparse=PREPARSE, semi_diacritics="ʃs")[0]
                        gcid, name, source = abb2lang[abb]
                        if cog.strip().lower() != 'na':
                            cogid = slug(concept)+'-'+cog
                        else:
                            cogid = str(cogidx)
                            cogidx += 1
                        
                        
                        if source not in visited_sources:
                            ds.sources.add(getEvoBibAsSource(source))
                            visited_sources += [source]

                        ds.add_row([
                            idx, gcid, name, '', cid, concept, word, source, segments,
                            cogid])
                        cognates += [[idx, ds.name,
                            word, cogid, '', 'expert', PROVIDER, '', '', '']]
                        idx += 1
    dataset.cognates.extend(iter_alignments(ds, cognates,
        method='progressive', ))
