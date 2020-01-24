# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from codeprep.parse.core import convert_text
from codeprep.tokens.containers import SplitContainer, StringLiteral, OneLineComment, MultilineComment
from codeprep.tokens.numeric import Number
from codeprep.tokens.whitespace import Tab, NewLine, SpaceInString
from codeprep.tokens.word import Word, Underscore, KeyWord, Operator, NonCodeChar, OpeningCurlyBracket, \
    ClosingCurlyBracket, Semicolon, OpeningBracket, ClosingBracket


def test_longs():
    text = '''long[] lovely_longs = {0x34a35EL,     0x88bc96fl           , -0x34L};'''
    expected_result = [KeyWord('long'),
                       Operator('['),
                       Operator(']'),
                       SplitContainer([Word.from_('lovely'),
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

    assert expected_result == actual


def test_ints():
    text = '''int[] _my_favoRite_ints_ = {0x12, 0x1fE, 441, -81, -0xfFf};'''

    expected_result = [KeyWord('int'),
                       Operator('['),
                       Operator(']'),
                       SplitContainer(
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

    assert expected_result == actual


def test_floats():
    text = '''float[] floats = {-0.43E4f, .58F, 0.d, -9.63e+2D, 0.E-8};'''
    expected_result = [KeyWord('float'),
                       Operator('['),
                       Operator(']'),
                       SplitContainer.from_single_token('floats'),
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

    assert expected_result == actual
    

def test_complex_identifiers():
    text = '''BigAWESOMEString[] a2y = "abc".doSplit("\\"");'''
    expected_result = [SplitContainer(
        [Word.from_('Big'), Word.from_('AWESOME'), Word.from_('String')], ),
        Operator('['),
        Operator(']'),
        SplitContainer([Word.from_('a'), Word.from_('2'), Word.from_('y')]),
        Operator('='),
        StringLiteral([NonCodeChar('"'), SplitContainer.from_single_token('abc'), NonCodeChar('"')], 5),
        Operator('.'),
        SplitContainer([Word.from_('do'), Word.from_('Split')]),
        OpeningBracket(),
        StringLiteral([NonCodeChar('"'), NonCodeChar('\\'), NonCodeChar('"'), NonCodeChar('"')], 4),
        ClosingBracket(),
        Semicolon(),
        NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert expected_result == actual


def test_string_with_spaces():
    text='''"hi   dear     world    !"'''
    expected = [StringLiteral([
        NonCodeChar('"'),
        SplitContainer.from_single_token('hi'),
        SpaceInString(3),
        SplitContainer.from_single_token('dear'),
        SpaceInString(5),
        SplitContainer.from_single_token('world'),
        SpaceInString(4),
        NonCodeChar('!'),
        NonCodeChar('"'),
    ], 26), NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert expected == actual


def test_spaces_in_strings():
    text = '''BigAWESOMEString[] a2y = "a    bc".doSplit("\\"");'''
    expected_result = [SplitContainer(
        [Word.from_('Big'), Word.from_('AWESOME'), Word.from_('String')], ),
        Operator('['),
        Operator(']'),
        SplitContainer([Word.from_('a'), Word.from_('2'), Word.from_('y')]),
        Operator('='),
        StringLiteral([NonCodeChar('"'),
                       SplitContainer.from_single_token('a'),
                       SpaceInString(n_chars=4),
                       SplitContainer.from_single_token('bc'),
                       NonCodeChar('"')],
                      9),
        Operator('.'),
        SplitContainer([Word.from_('do'), Word.from_('Split')]),
        OpeningBracket(),
        StringLiteral([NonCodeChar('"'), NonCodeChar('\\'), NonCodeChar('"'), NonCodeChar('"')], 4),
        ClosingBracket(),
        Semicolon(),
        NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert expected_result == actual
    

def test_one_line_comment():
    text = '''// this code won't compile but the preprocessing still has to be done corrrectly'''

    expected_result = [OneLineComment([NonCodeChar('/'), NonCodeChar('/'),
                                       SplitContainer.from_single_token('this'),
                                       SplitContainer.from_single_token('code'),
                                       SplitContainer.from_single_token('won'), NonCodeChar("'"),
                                       SplitContainer.from_single_token('t'),
                                       SplitContainer.from_single_token('compile'),
                                       SplitContainer.from_single_token('but'),
                                       SplitContainer.from_single_token('the'),
                                       SplitContainer.from_single_token('preprocessing'),
                                       SplitContainer.from_single_token('still'),
                                       SplitContainer.from_single_token('has'),
                                       SplitContainer.from_single_token('to'),
                                       SplitContainer.from_single_token('be'),
                                       SplitContainer.from_single_token('done'),
                                       SplitContainer.from_single_token('corrrectly'),
                                       NewLine()
                                       ])]

    actual = [t for t in convert_text(text, 'java')]

    assert expected_result == actual


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

    expected_result = [SplitContainer([Word.from_('abc'), Word.from_('1')]),
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

    assert expected_result == actual


def test_multi_line_comment():
    text = '''
/*multi-line MyComment_
*//
_operations
'''

    expected_result = [MultilineComment([NonCodeChar('/'), NonCodeChar('*'), SplitContainer.from_single_token('multi'), NonCodeChar('-'),
                                         SplitContainer.from_single_token('line'),
                                         SplitContainer([
                                             Word.from_('My'),
                                             Word.from_('Comment'),
                                             Underscore()
                                         ]),
                                         NewLine(), NonCodeChar('*'), NonCodeChar('/')]),
                       Operator('/'),
                       NewLine(),
                       SplitContainer([Underscore(), Word.from_('operations')]),
                       NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert expected_result == actual
    

def test_capitals():
    text = '''
MyClass Class CONSTANT VAR_WITH_UNDERSCORES
'''

    expected_result = [SplitContainer([Word.from_("My"), Word.from_("Class")]),
                       SplitContainer.from_single_token("Class"),
                       SplitContainer.from_single_token("CONSTANT"),
                       SplitContainer([Word.from_("VAR"),
                                       Underscore(),
                                       Word.from_("WITH"),
                                       Underscore(),
                                       Word.from_("UNDERSCORES")]),
                       NewLine()]

    actual = [t for t in convert_text(text, 'java')]

    assert expected_result == actual


def test_string_literal_single():
    text = '''a = 'some_text'.split()'''

    expected_result = [SplitContainer.from_single_token("a"),
                       Operator('='),
                       StringLiteral([NonCodeChar("'")], 1),
                       StringLiteral([SplitContainer([Word.from_("some"), Underscore(), Word.from_("text")])], 9),
                       StringLiteral([NonCodeChar("'")], 1),
                       Operator('.'),
                       SplitContainer.from_single_token("split"),
                       OpeningBracket(),
                       ClosingBracket(),
                       NewLine()
                       ]

    actual = [t for t in convert_text(text, 'py')]

    assert expected_result == actual


def test_string_literal_double():
    text = '''a = "some_text".split()'''

    expected_result = [SplitContainer.from_single_token("a"),
                       Operator('='),
                       StringLiteral([NonCodeChar('"')], 1),
                       StringLiteral([SplitContainer([Word.from_("some"), Underscore(), Word.from_("text")])], 9),
                       StringLiteral([NonCodeChar('"')], 1),
                       Operator('.'),
                       SplitContainer.from_single_token("split"),
                       OpeningBracket(),
                       ClosingBracket(),
                       NewLine()
                       ]

    actual = [t for t in convert_text(text, 'py')]

    assert expected_result == actual