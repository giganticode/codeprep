# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from codeprep.tokentypes.numeric import Number

from codeprep.parse.matchers import split_into_words
from codeprep.tokentypes.containers import Identifier
from codeprep.tokentypes.whitespace import NewLine, SpaceInString
from codeprep.tokentypes.word import Word, Underscore
from codeprep.parse.subtokens import split_string


def test_split_into_tokens():
    actual = split_into_words("123\nAb2cd34Ef000GG j_89_J")

    expected = [Number('123'),
                NewLine(),
                Identifier([Word.from_('Ab'), Word.from_('2'), Word.from_('cd'),
                            Word.from_('34'), Word.from_('Ef'), Word.from_('000'), Word.from_('GG')]),
                Identifier([Word.from_('j'), Underscore(), Word.from_('89'), Underscore(), Word.from_('J')])]

    assert actual == expected


def test_split_string():
    actual = split_string("123\nAb2cd34Ef000GG     j_89_J")

    expected = [Number('123'),
                NewLine(),
                Identifier([Word.from_('Ab'), Word.from_('2'), Word.from_('cd'),
                            Word.from_('34'), Word.from_('Ef'), Word.from_('000'), Word.from_('GG')]),
                SpaceInString(5),
                Identifier([Word.from_('j'), Underscore(), Word.from_('89'), Underscore(), Word.from_('J')])]

    assert actual == expected