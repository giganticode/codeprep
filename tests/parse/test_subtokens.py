from dataprep.tokens.numeric import Number

from dataprep.parse.matchers import split_into_words
from dataprep.tokens.containers import SplitContainer
from dataprep.tokens.whitespace import NewLine, SpaceInString
from dataprep.tokens.word import Word, Underscore
from dataprep.parse.subtokens import split_string


def test_split_into_tokens():
    actual = split_into_words("123\nAb2cd34Ef000GG j_89_J")

    expected = [Number('123'),
                NewLine(),
                SplitContainer([Word.from_('Ab'), Word.from_('2'), Word.from_('cd'),
                                Word.from_('34'), Word.from_('Ef'), Word.from_('000'), Word.from_('GG')]),
                SplitContainer([Word.from_('j'), Underscore(), Word.from_('89'), Underscore(), Word.from_('J')])]

    assert expected == actual


def test_split_string():
    actual = split_string("123\nAb2cd34Ef000GG     j_89_J")

    expected = [Number('123'),
                NewLine(),
                SplitContainer([Word.from_('Ab'), Word.from_('2'), Word.from_('cd'),
                                Word.from_('34'), Word.from_('Ef'), Word.from_('000'), Word.from_('GG')]),
                SpaceInString(5),
                SplitContainer([Word.from_('j'), Underscore(), Word.from_('89'), Underscore(), Word.from_('J')])]

    assert expected == actual
