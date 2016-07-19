# coding: utf8
from __future__ import unicode_literals, print_function, division

from nose.tools import assert_equal

from pylexibank import util


def test_split():
    for string, res in [
        ("abc", [('abc', None)]),
        ("abc,def", [('abc', None), ('def', None)]),
        ("ab(c,def)", [('ab(c,def)', None)]),
        ("*küm- die, (fire) goes out", [('*küm- die', None), ('goes out', '(fire)')]),
        ("*(ŋg,k)iti [maŋgV]", [('*(ŋg,k)iti', '[maŋgV]')]),
        ("(ba-)hi, hián [puhiu =drink water; hiáhí- drink -Lionnet]",
         [('(ba-)hi', None), ('hián', '[puhiu =drink water; hiáhí- drink -Lionnet]')]),
        ("*[ji(C)]-ha(d,l)ug", [('*[ji(C)]-ha(d,l)ug', None)]),
    ]:
        yield check_split, string, res


def check_split(string, expected):
    assert_equal(list(util.split(string)), expected)
