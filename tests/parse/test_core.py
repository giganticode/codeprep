# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from codeprep.parse.core import convert_text
from codeprep.tokentypes.containers import Identifier, StringLiteral, OneLineComment, MultilineComment
from codeprep.tokentypes.numeric import Number
from codeprep.tokentypes.whitespace import Tab, NewLine, SpaceInString
from codeprep.tokentypes.word import Word, Underscore, KeyWord, Operator, NonCodeChar, OpeningCurlyBracket, \
    ClosingCurlyBracket, Semicolon, OpeningBracket, ClosingBracket, StringLiteralQuote


def test_longs():
    text = '''long[] lovely_longs = {0x34a35EL,     0x88bc96fl           , -0x34L};'''
    expected_result = [KeyWord('long'),
                       Operator('['),
                       Operator(']'),
                       Identifier([Word.from_('lovely'),
                                   Underscore(),
                                   Word.from_('longs')]),
                       Operator('='),
                       OpeningCurlyBracket(),
                       Number("0x34a35EL"),
                       Operator(','),
                       Tab(),
                       Number("0x88bc96fl"),
                       Tab(),
                       Tab(),
                       Operator(','),
                       Operator('-'),
                       Number("0x34L"),
                       ClosingCurlyBracket(),
                       Semicolon(), NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert actual == expected_result


def test_ints():
    text = '''int[] _my_favoRite_ints_ = {0x12, 0x1fE, 441, -81, -0xfFf};'''

    expected_result = [KeyWord('int'),
                       Operator('['),
                       Operator(']'),
                       Identifier(
                           [Underscore(),
                            Word.from_('my'),
                            Underscore(),
                            Word.from_('favo'),
                            Word.from_('Rite'),
                            Underscore(),
                            Word.from_('ints'),
                            Underscore()]
                       ),
                       Operator('='),
                       OpeningCurlyBracket(),
                       Number("0x12"),
                       Operator(','),
                       Number("0x1fE"),
                       Operator(','),
                       Number("441"),
                       Operator(','),
                       Operator('-'),
                       Number("81"),
                       Operator(','),
                       Operator('-'),
                       Number("0xfFf"),
                       ClosingCurlyBracket(),
                       Semicolon(),
                       NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert actual == expected_result


def test_floats():
    text = '''float[] floats = {-0.43E4f, .58F, 0.d, -9.63e+2D, 0.E-8};'''
    expected_result = [KeyWord('float'),
                       Operator('['),
                       Operator(']'),
                       Identifier.from_single_token('floats'),
                       Operator('='),
                       OpeningCurlyBracket(),
                       Operator('-'),
                       Number("0.43E4f"),
                       Operator(','),
                       Number(".58F"),
                       Operator(','),
                       Number("0.d"),
                       Operator(','),
                       Operator('-'),
                       Number('9.63e+2D'),
                       Operator(','),
                       Number('0.E-8'),
                       ClosingCurlyBracket(),
                       Semicolon(),
                       NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert actual == expected_result


def test_complex_identifiers():
    text = '''BigAWESOMEString[] a2y = "abc".doSplit("\\"");'''
    expected_result = [Identifier(
        [Word.from_('Big'), Word.from_('AWESOME'), Word.from_('String')], ),
        Operator('['),
        Operator(']'),
        Identifier([Word.from_('a'), Word.from_('2'), Word.from_('y')]),
        Operator('='),
        StringLiteralQuote('"'),
        StringLiteral([Identifier.from_single_token('abc')], 3),
        StringLiteralQuote('"'),
        Operator('.'),
        Identifier([Word.from_('do'), Word.from_('Split')]),
        OpeningBracket(),
        StringLiteralQuote('"'),
        StringLiteral([NonCodeChar('\\'), NonCodeChar('"')], 2),
        StringLiteralQuote('"'),
        ClosingBracket(),
        Semicolon(),
        NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert actual == expected_result


def test_string_with_spaces():
    text='''"hi   dear     world    !"'''
    expected = [
        StringLiteralQuote('"'),
        StringLiteral([
            Identifier.from_single_token('hi'),
            SpaceInString(3),
            Identifier.from_single_token('dear'),
            SpaceInString(5),
            Identifier.from_single_token('world'),
            SpaceInString(4),
            NonCodeChar('!')], 24),
        StringLiteralQuote('"'),
        NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert actual == expected


def test_spaces_in_strings():
    text = '''BigAWESOMEString[] a2y = "a    bc".doSplit("\\"");'''
    expected_result = [Identifier(
        [Word.from_('Big'), Word.from_('AWESOME'), Word.from_('String')], ),
        Operator('['),
        Operator(']'),
        Identifier([Word.from_('a'), Word.from_('2'), Word.from_('y')]),
        Operator('='),
        StringLiteralQuote('"'),
        StringLiteral([
            Identifier.from_single_token('a'),
            SpaceInString(n_chars=4),
            Identifier.from_single_token('bc')], 7),
        StringLiteralQuote('"'),
        Operator('.'),
        Identifier([Word.from_('do'), Word.from_('Split')]),
        OpeningBracket(),
        StringLiteralQuote('"'),
        StringLiteral([NonCodeChar('\\'), NonCodeChar('"')], 2),
        StringLiteralQuote('"'),
        ClosingBracket(),
        Semicolon(),
        NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert actual == expected_result


def test_one_line_comment():
    text = '''// this code won't compile but the preprocessing still has to be done corrrectly'''

    expected_result = [OneLineComment([NonCodeChar('/'), NonCodeChar('/'),
                                       Identifier.from_single_token('this'),
                                       Identifier.from_single_token('code'),
                                       Identifier.from_single_token('won'), NonCodeChar("'"),
                                       Identifier.from_single_token('t'),
                                       Identifier.from_single_token('compile'),
                                       Identifier.from_single_token('but'),
                                       Identifier.from_single_token('the'),
                                       Identifier.from_single_token('preprocessing'),
                                       Identifier.from_single_token('still'),
                                       Identifier.from_single_token('has'),
                                       Identifier.from_single_token('to'),
                                       Identifier.from_single_token('be'),
                                       Identifier.from_single_token('done'),
                                       Identifier.from_single_token('corrrectly'),
                                       NewLine()
                                       ])]

    actual = [t for t in convert_text(text, 'java')]

    assert actual == expected_result


def test_special_characters():
    text = '''
abc1
~-0xFFFFFL=
.0E+5
|=
?
==
!=
**
++
--
+=
-=
/=
*=
%=
$
<=
>=
@
    ^=
    &=
    #
                                                                                 >>
<<
&&
||
+*!/><\t\n
{}[],.-:();&|\\'~%^
'''

    expected_result = [Identifier([Word.from_('abc'), Word.from_('1')]),
                       NewLine(),
                       Operator('~'),
                       Operator('-'),
                       Number("0xFFFFFL"),
                       Operator('='),
                       NewLine(),
                       Number(".0E+5"),
                       NewLine(),
                       Operator('|'), Operator('='),
                       NewLine(),
                       Operator('?'),
                       NewLine(),
                       Operator('='), Operator('='),
                       NewLine(),
                       Operator('!'), Operator('='),
                       NewLine(),
                       Operator('*'), Operator('*'),
                       NewLine(),
                       Operator('+'), Operator('+'),
                       NewLine(),
                       Operator('-'), Operator('-'),
                       NewLine(),
                       Operator('+'), Operator('='),
                       NewLine(),
                       Operator('-'), Operator('='),
                       NewLine(),
                       Operator('/'), Operator('='),
                       NewLine(),
                       Operator('*'), Operator('='),
                       NewLine(),
                       Operator('%'), Operator('='),
                       NewLine(),
                       NonCodeChar('$'),
                       NewLine(),
                       Operator('<'), Operator('='),
                       NewLine(),
                       Operator('>'), Operator('='),
                       NewLine(),
                       NonCodeChar('@'),
                       NewLine(),
                       Tab(),
                       Operator('^'), Operator('='),
                       NewLine(),
                       Tab(),
                       Operator('&'), Operator('='),
                       NewLine(),
                       Tab(),
                       NonCodeChar('#'),
                       NewLine(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Tab(),
                       Operator('>'), Operator('>'),
                       NewLine(),
                       Operator('<'), Operator('<'),
                       NewLine(),
                       Operator('&'), Operator('&'),
                       NewLine(),
                       Operator('|'), Operator('|'),
                       NewLine(),
                       Operator('+'),
                       Operator('*'),
                       Operator('!'),
                       Operator('/'),
                       Operator('>'),
                       Operator('<'),
                       Tab(),
                       NewLine(),
                       NewLine(),
                       OpeningCurlyBracket(),
                       ClosingCurlyBracket(),
                       Operator('['),
                       Operator(']'),
                       Operator(','),
                       Operator('.'),
                       Operator('-'),
                       Operator(':'),
                       OpeningBracket(),
                       ClosingBracket(),
                       Semicolon(),
                       Operator('&'),
                       Operator('|'),
                       NonCodeChar('\\'),
                       NonCodeChar("'"),
                       Operator('~'),
                       Operator('%'),
                       Operator('^'),
                       NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert actual == expected_result


def test_multi_line_comment():
    text = '''
/*multi-line MyComment_
*//
_operations
'''

    expected_result = [MultilineComment([NonCodeChar('/'), NonCodeChar('*'), Identifier.from_single_token('multi'), NonCodeChar('-'),
                                         Identifier.from_single_token('line'),
                                         Identifier([
                                             Word.from_('My'),
                                             Word.from_('Comment'),
                                             Underscore()
                                         ]),
                                         NewLine(), NonCodeChar('*'), NonCodeChar('/')]),
                       Operator('/'),
                       NewLine(),
                       Identifier([Underscore(), Word.from_('operations')]),
                       NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert actual == expected_result


def test_capitals():
    text = '''
MyClass Class CONSTANT VAR_WITH_UNDERSCORES
'''

    expected_result = [Identifier([Word.from_("My"), Word.from_("Class")]),
                       Identifier.from_single_token("Class"),
                       Identifier.from_single_token("CONSTANT"),
                       Identifier([Word.from_("VAR"),
                                   Underscore(),
                                   Word.from_("WITH"),
                                   Underscore(),
                                   Word.from_("UNDERSCORES")]),
                       NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert actual == expected_result


def test_string_literal_single():
    text = '''a = 'some_text'.split()'''

    expected_result = [Identifier.from_single_token("a"),
                       Operator('='),
                       StringLiteralQuote("'"),
                       StringLiteral([Identifier([Word.from_("some"), Underscore(), Word.from_("text")])], 9),
                       StringLiteralQuote("'"),
                       Operator('.'),
                       Identifier.from_single_token("split"),
                       OpeningBracket(),
                       ClosingBracket(),
                       NewLine()
                       ]

    actual = [t for t in convert_text(text, 'py')]

    assert actual == expected_result


def test_string_literal_double():
    text = '''a = "some_text".split()'''

    expected_result = [Identifier.from_single_token("a"),
                       Operator('='),
                       StringLiteralQuote('"'),
                       StringLiteral([Identifier([Word.from_("some"), Underscore(), Word.from_("text")])], 9),
                       StringLiteralQuote('"'),
                       Operator('.'),
                       Identifier.from_single_token("split"),
                       OpeningBracket(),
                       ClosingBracket(),
                       NewLine()
                       ]

    actual = [t for t in convert_text(text, 'py')]

    assert actual == expected_result