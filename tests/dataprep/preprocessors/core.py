import unittest

from dataprep.model.word import Word, Underscore
from dataprep.preprocessors.preprocessor_list import pp_params
from dataprep.preprocessors.core import apply_preprocessors, from_lines
from dataprep.model.chars import NewLine, Tab, Backslash, Quote
from dataprep.model.containers import OneLineComment, SplitContainer, StringLiteral, MultilineComment
from dataprep.model.numeric import HexStart, Number, DecimalPoint, L, F, E, D

text2 = '''
_my_favoRite_ints_
'''

text3 = '''" RegisterImage "'''


# print(dd)

class ApplyPreprocessorsTest(unittest.TestCase):
    def __test_apply_preprocessors(self, input, expected):
        res = apply_preprocessors(from_lines([l for l in input.split("\n")]), pp_params["preprocessors"])
        self.assertEqual(expected, res)

    def test_1(self):
        text = '''
long[] lovely_longs = {0x34a35EL,     0x88bc96fl           , -0x34L};
'''
        expected_result = [NewLine(),
                           SplitContainer.from_single_token('long'),
                           '[',
                           ']',
                           SplitContainer([Word.from_('lovely'),
                                           Underscore(),
                                           Word.from_('longs')]),
                           '=',
                           '{',
                           Number([HexStart(), '3', '4', 'a', '3', '5', 'E', L()]),
                           ',',
                           Tab(),
                           Number([HexStart(), '8', '8', 'b', 'c', '9', '6', 'f', L()]),
                           Tab(),
                           Tab(),
                           ',',
                           Number(['-', HexStart(), '3', '4', L()]),
                           '}',
                           ';',
                           NewLine(), NewLine()]

        self.__test_apply_preprocessors(text, expected_result)

    def test_2(self):
        text = '''
int[] _my_favoRite_ints_ = {0x12, 0x1fE, 441, -81, -0xfFf};
'''
        expected_result = [NewLine(),
                           SplitContainer.from_single_token('int'),
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
                           Number([HexStart(), '1', '2']),
                           ',',
                           Number([HexStart(), '1', 'f', 'E']),
                           ',',
                           Number(['4', '4', '1']),
                           ',',
                           Number(['-', '8', '1']),
                           ',',
                           Number(['-', HexStart(), 'f', 'F', 'f']),
                           '}',
                           ';',
                           NewLine(), NewLine()]

        self.__test_apply_preprocessors(text, expected_result)

    def test_3(self):
        text = '''
float[] floats = {-0.43E4f, .58F, 0.d, -9.63e+2D, 0.E-8};
'''
        expected_result = [NewLine(),
                           SplitContainer.from_single_token('float'),
                           '[',
                           ']',
                           SplitContainer.from_single_token('floats'),
                           '=',
                           '{',
                           Number(['-', '0', DecimalPoint(), '4', '3', E(), '4', F()]),
                           ',',
                           Number([DecimalPoint(), '5', '8', F()]),
                           ',',
                           Number(['0', DecimalPoint(), D()]),
                           ',',
                           Number(['-', '9', DecimalPoint(), '6', '3', E(), '+', '2', D()]),
                           ',',
                           Number(['0', DecimalPoint(), E(), '-', '8']),
                           '}',
                           ';',
                           NewLine(), NewLine()]

        self.__test_apply_preprocessors(text, expected_result)

    def test_4(self):
        text = '''
BigAWESOMEString[] a2y = "abc".doSplit("\\"");
'''
        expected_result = [NewLine(), SplitContainer(
            [Word.from_('Big'), Word.from_('AWESOME'), Word.from_('String')]),
                           '[',
                           ']',
                           SplitContainer([Word.from_('a'), Word.from_('2'), Word.from_('y')]),
                           '=',
                           StringLiteral([SplitContainer.from_single_token('abc')]),
                           '.',
                           SplitContainer([Word.from_('do'), Word.from_('Split')]),
                           '(',
                           StringLiteral([Backslash(), Quote()]),
                           ')',
                           ';',
                           NewLine(), NewLine()]

        self.__test_apply_preprocessors(text, expected_result)

    def test_5(self):
        text = '''
// this code won't compile but the preprocessing still has to be done corrrectly
'''
        expected_result = [NewLine(), OneLineComment([SplitContainer.from_single_token('this'),
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
                                                      SplitContainer.from_single_token('corrrectly')]),
                           NewLine(), NewLine()]

        self.__test_apply_preprocessors(text, expected_result)

    def test_6(self):
        text = '''
9a abc1
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

        expected_result = [NewLine(),
                           SplitContainer([Word.from_('9'), Word.from_('a')]),
                           SplitContainer([Word.from_('abc'), Word.from_('1')]),
                           NewLine(),
                           '~',
                           Number(['-', HexStart(), 'F', 'F', 'F', 'F', 'F', L()]),
                           '=',
                           NewLine(),
                           Number([DecimalPoint(), '0', E(), '+', '5']),
                           NewLine(),
                           '|=',
                           NewLine(),
                           '?',
                           NewLine(),
                           '==',
                           NewLine(),
                           '!=',
                           NewLine(),
                           '**',
                           NewLine(),
                           '++',
                           NewLine(),
                           '--',
                           NewLine(),
                           '+=',
                           NewLine(),
                           '-=',
                           NewLine(),
                           '/=',
                           NewLine(),
                           '*=',
                           NewLine(),
                           '%=',
                           NewLine(),
                           '$',
                           NewLine(),
                           '<=',
                           NewLine(),
                           '>=',
                           NewLine(),
                           '@',
                           NewLine(),
                           Tab(),
                           '^=',
                           NewLine(),
                           Tab(),
                           '&=',
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
                           '>>',
                           NewLine(),
                           '<<',
                           NewLine(),
                           '&&',
                           NewLine(),
                           '||',
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
                           Backslash(),
                           "'",
                           '~',
                           '%',
                           '^',
                           NewLine(), NewLine()]

        self.__test_apply_preprocessors(text, expected_result)

    def test_7(self):
        text = '''
/*multi-line MyComment_
*//
_operations
'''

        expected_result = [NewLine(),
                           MultilineComment([SplitContainer.from_single_token('multi'), '-',
                                             SplitContainer.from_single_token('line'),
                                             SplitContainer([
                                                 Word.from_('My'),
                                                 Word.from_('Comment'),
                                                 Underscore()
                                             ]),
                                             NewLine()]),
                           '/',
                           NewLine(),
                           SplitContainer([Underscore(), Word.from_('operations')]),
                           NewLine(),
                           NewLine()]

        self.__test_apply_preprocessors(text, expected_result)

    def test_capitals(self):
        text = '''
MyClass Class CONSTANT VAR_WITH_UNDERSCORES
'''

        expected_result = [NewLine(),
                           SplitContainer([Word.from_("My"), Word.from_("Class")]),
                           SplitContainer.from_single_token("Class"),
                           SplitContainer.from_single_token("CONSTANT"),
                           SplitContainer([Word.from_("VAR"),
                                           Underscore(),
                                           Word.from_("WITH"),
                                           Underscore(),
                                           Word.from_("UNDERSCORES")]),
                           NewLine(), NewLine()]

        self.__test_apply_preprocessors(text, expected_result)


if __name__ == '__main__':
    unittest.main()
