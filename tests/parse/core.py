import unittest

from dataprep.parse.core import convert_text
from dataprep.parse.model.containers import SplitContainer, StringLiteral, OneLineComment, MultilineComment
from dataprep.parse.model.numeric import Number
from dataprep.parse.model.whitespace import Tab, NewLine
from dataprep.parse.model.word import Word, Underscore


class ConvertTextTest(unittest.TestCase):

    def test_longs(self):
        text = '''long[] lovely_longs = {0x34a35EL,     0x88bc96fl           , -0x34L};'''
        print(text)
        expected_result = ['long',
                           '[',
                           ']',
                           SplitContainer([Word.from_('lovely'),
                                           Underscore(),
                                           Word.from_('longs')]),
                           '=',
                           '{',
                           Number(['0', 'x', '3', '4', 'a', '3', '5', 'E', 'L']),
                           ',',
                           Tab(),
                           Number(['0', 'x', '8', '8', 'b', 'c', '9', '6', 'f', 'l']),
                           Tab(),
                           Tab(),
                           ',',
                           '-',
                           Number(['0', 'x', '3', '4', 'L']),
                           '}',
                           ';', NewLine()]


        actual = [t for t in convert_text(text, 'java')]

        self.assertEqual(expected_result, actual)

    def test_ints(self):
        text = '''int[] _my_favoRite_ints_ = {0x12, 0x1fE, 441, -81, -0xfFf};'''

        expected_result = ['int',
                           '[',
                           ']',
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
                           '=',
                           '{',
                           Number(['0', 'x', '1', '2']),
                           ',',
                           Number(['0', 'x', '1', 'f', 'E']),
                           ',',
                           Number(['4', '4', '1']),
                           ',',
                           '-',
                           Number(['8', '1']),
                           ',',
                           '-',
                           Number(['0', 'x', 'f', 'F', 'f']),
                           '}',
                           ';',
                           NewLine()]

        actual = [t for t in convert_text(text, 'java')]

        self.assertEqual(expected_result, actual)

    def test_floats(self):
        text = '''float[] floats = {-0.43E4f, .58F, 0.d, -9.63e+2D, 0.E-8};'''
        expected_result = ['float',
                           '[',
                           ']',
                           SplitContainer.from_single_token('floats'),
                           '=',
                           '{',
                           '-',
                           Number(['0', '.', '4', '3', 'E', '4', 'f']),
                           ',',
                           Number(['.', '5', '8', 'F']),
                           ',',
                           Number(['0', '.', 'd']),
                           ',',
                           '-',
                           Number(['9', '.', '6', '3', 'e', '+', '2', 'D']),
                           ',',
                           Number(['0', '.', 'E', '-', '8']),
                           '}',
                           ';',
                           NewLine()]

        actual = [t for t in convert_text(text, 'java')]

        self.assertEqual(expected_result, actual)

    def test_complex_identifiers(self):
        text = '''BigAWESOMEString[] a2y = "abc".doSplit("\\"");'''
        expected_result = [SplitContainer(
            [Word.from_('Big'), Word.from_('AWESOME'), Word.from_('String')]),
            '[',
            ']',
            SplitContainer([Word.from_('a'), Word.from_('2'), Word.from_('y')]),
            '=',
            StringLiteral(['"', SplitContainer.from_single_token('abc'), '"']),
            '.',
            SplitContainer([Word.from_('do'), Word.from_('Split')]),
            '(',
            StringLiteral(['"', '\\', '"', '"']),
            ')',
            ';',
            NewLine()]

        actual = [t for t in convert_text(text, 'java')]

        self.assertEqual(expected_result, actual)

    def test_one_line_comment(self):
        text = '''// this code won't compile but the preprocessing still has to be done corrrectly'''

        expected_result = [OneLineComment(['/', '/',
                                           SplitContainer.from_single_token('this'),
                                           SplitContainer.from_single_token('code'),
                                           SplitContainer.from_single_token('won'), "'",
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

        self.assertEqual(expected_result, actual)

    def test_special_characters(self):
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
                           '~',
                           '-',
                           Number(['0', 'x', 'F', 'F', 'F', 'F', 'F', 'L']),
                           '=',
                           NewLine(),
                           Number(['.', '0', 'E', '+', '5']),
                           NewLine(),
                           '|', '=',
                           NewLine(),
                           '?',
                           NewLine(),
                           '=', '=',
                           NewLine(),
                           '!', '=',
                           NewLine(),
                           '*', '*',
                           NewLine(),
                           '+', '+',
                           NewLine(),
                           '-', '-',
                           NewLine(),
                           '+', '=',
                           NewLine(),
                           '-', '=',
                           NewLine(),
                           '/', '=',
                           NewLine(),
                           '*', '=',
                           NewLine(),
                           '%', '=',
                           NewLine(),
                           '$',
                           NewLine(),
                           '<', '=',
                           NewLine(),
                           '>', '=',
                           NewLine(),
                           '@',
                           NewLine(),
                           Tab(),
                           '^', '=',
                           NewLine(),
                           Tab(),
                           '&', '=',
                           NewLine(),
                           Tab(),
                           '#',
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
                           '>', '>',
                           NewLine(),
                           '<', '<',
                           NewLine(),
                           '&', '&',
                           NewLine(),
                           '|', '|',
                           NewLine(),
                           '+',
                           '*',
                           '!',
                           '/',
                           '>',
                           '<',
                           Tab(),
                           NewLine(),
                           NewLine(),
                           '{',
                           '}',
                           '[',
                           ']',
                           ',',
                           '.',
                           '-',
                           ':',
                           '(',
                           ')',
                           ';',
                           '&',
                           '|',
                           '\\',
                           "'",
                           '~',
                           '%',
                           '^',
                           NewLine()]

        actual = [t for t in convert_text(text, 'java')]

        self.assertEqual(expected_result, actual)

    def test_multi_line_comment(self):
        text = '''
/*multi-line MyComment_
*//
_operations
'''

        expected_result = [MultilineComment(['/', '*', SplitContainer.from_single_token('multi'), '-',
                                             SplitContainer.from_single_token('line'),
                                             SplitContainer([
                                                 Word.from_('My'),
                                                 Word.from_('Comment'),
                                                 Underscore()
                                             ]),
                                             NewLine(), '*', '/']),
                           '/',
                           NewLine(),
                           SplitContainer([Underscore(), Word.from_('operations')]),
                           NewLine()]

        actual = [t for t in convert_text(text, 'java')]

        self.assertEqual(expected_result, actual)

    def test_capitals(self):
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

        self.assertEqual(expected_result, actual)

    def test_string_literal_single(self):
        text = '''a = 'some_text'.split()'''

        expected_result = [SplitContainer.from_single_token("a"),
                           '=',
                           StringLiteral(["'"]),
                           StringLiteral([SplitContainer([Word.from_("some"), Underscore(), Word.from_("text")])]),
                           StringLiteral(["'"]),
                           '.',
                           SplitContainer.from_single_token("split"),
                           "(",
                           ")",
                           NewLine()
                           ]

        actual = [t for t in convert_text(text, 'py')]

        self.assertEqual(expected_result, actual)

    def test_string_literal_double(self):
        text = '''a = "some_text".split()'''

        expected_result = [SplitContainer.from_single_token("a"),
                           '=',
                           StringLiteral(['"']),
                           StringLiteral([SplitContainer([Word.from_("some"), Underscore(), Word.from_("text")])]),
                           StringLiteral(['"']),
                           '.',
                           SplitContainer.from_single_token("split"),
                           "(",
                           ")",
                           NewLine()
                           ]

        actual = [t for t in convert_text(text, 'py')]

        self.assertEqual(expected_result, actual)


if __name__ == '__main__':
    unittest.main()
