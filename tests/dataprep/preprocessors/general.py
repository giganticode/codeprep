import unittest

from dataprep.preprocessors.general import spl_verbose
from dataprep.model.chars import MultilineCommentStart, MultilineCommentEnd, OneLineCommentStart, \
    Quote, Backslash, Tab
from dataprep.model.word import ParseableToken


class GeneralTest(unittest.TestCase):
    def test_split_verbose1(self):
        text = '''
long[] lovely_longs = {/* there should be some longs here*/};
int[] _my_favoRite_ints_ = {/* ints here*/};
'''
        actual = spl_verbose([ParseableToken(text)])

        expected = ['\n', ParseableToken("long"), '[', ']', ParseableToken("lovely_longs"),
                    '=', '{', MultilineCommentStart(),
                    ParseableToken("there"),
                    ParseableToken("should"),
                    ParseableToken("be"),
                    ParseableToken("some"),
                    ParseableToken("longs"),
                    ParseableToken("here"),
                    MultilineCommentEnd(), "}", ';', '\n',
                    ParseableToken("int"),
                    '[', ']', ParseableToken("_my_favoRite_ints_"), '=', '{', MultilineCommentStart(),
                    ParseableToken("ints"), ParseableToken("here"), MultilineCommentEnd(), '}', ';', '\n',
                    ]

        self.assertEqual(expected, actual)

    def test_split_verbose2(self):
        text='''
float[] floats = {}; //floats were removed 
BigAWESOMEString[] a2y = "abc".doSplit("\\"");
'''
        actual = spl_verbose([ParseableToken(text)])

        expected = ['\n', ParseableToken("float"), '[', ']', ParseableToken("floats"), '=', '{', '}',
                    ';', OneLineCommentStart(), ParseableToken("floats"), ParseableToken("were"),
                    ParseableToken("removed"), '\n', ParseableToken("BigAWESOMEString"),
                    '[', ']', ParseableToken("a2y"), '=', Quote(), ParseableToken("abc"), Quote(), '.',
                    ParseableToken("doSplit"), '(', Quote(), Backslash(), Quote(), Quote(), ')', ';', '\n', ]

        self.assertEqual(expected, actual)

    def test_split_verbose3(self):
        text = '''
// this code won't compile but the preprocessing still has to be done corrrectly
9a ** abc1
~-|=?==!=/* gj **/
'''
        actual = spl_verbose([ParseableToken(text)])

        expected = ['\n', OneLineCommentStart(),
                    ParseableToken("this"), ParseableToken("code"), ParseableToken("won"),
                    "'", ParseableToken("t"), ParseableToken("compile"), ParseableToken("but"),
                    ParseableToken("the"), ParseableToken("preprocessing"), ParseableToken("still"),
                    ParseableToken("has"), ParseableToken("to"), ParseableToken("be"),
                    ParseableToken("done"), ParseableToken("corrrectly"), '\n',
                    ParseableToken("9a"), '**', ParseableToken("abc1"), '\n', '~', '-', '|=', '?',
                    '==', '!=', MultilineCommentStart(), ParseableToken("gj"), '*',
                    MultilineCommentEnd(), '\n']

        self.assertEqual(expected, actual)

    def test_split_verbose4(self):
        text = '''
a++a
b--b
c+=c
d-=d
e/=e
f*=f
g%=g
h$h
i<=i
j>=j
k@k
    l^=l
    m&=m
    n#n
                                                                    o>>o
p<<p
q&&q
r||r
+*!/><\t\n
{}[],.-:();&|\\'~%^
/*multi-line MyComment_
*//
_operations
'''
        actual = spl_verbose([ParseableToken(text)])

        expected = ['\n', ParseableToken('a'), '++', ParseableToken('a'),
                    '\n', ParseableToken('b'), '--', ParseableToken('b'),
                    '\n', ParseableToken('c'), '+=', ParseableToken('c'),
                    '\n', ParseableToken('d'), '-=', ParseableToken('d'),
                    '\n', ParseableToken('e'), '/=', ParseableToken('e'),
                    '\n', ParseableToken('f'), '*=', ParseableToken('f'),
                    '\n', ParseableToken('g'), '%=', ParseableToken('g'),
                    '\n', ParseableToken('h'), '$', ParseableToken('h'),
                    '\n', ParseableToken('i'), '<=', ParseableToken('i'),
                    '\n', ParseableToken('j'), '>=', ParseableToken('j'),
                    '\n', ParseableToken('k'), '@', ParseableToken('k'),
                    '\n', ParseableToken('l'), '^=', ParseableToken('l'),
                    '\n', ParseableToken('m'), '&=', ParseableToken('m'),
                    '\n', ParseableToken('n'), '#', ParseableToken('n'),
                    '\n', ParseableToken('o'), '>>', ParseableToken('o'),
                    '\n', ParseableToken('p'), '<<', ParseableToken('p'),
                    '\n', ParseableToken('q'), '&&', ParseableToken('q'),
                    '\n', ParseableToken('r'), '||', ParseableToken('r'),
                    '\n', '+', '*', '!', '/', '>', '<', Tab(), '\n', '\n', '{', '}', '[',
                    ']', ',', '.', '-', ':', '(', ')', ';', '&', '|', Backslash(), "'", '~', '%', '^',
                    '\n', MultilineCommentStart(), ParseableToken("multi"), '-', ParseableToken("line"),
                    ParseableToken("MyComment_"), '\n', MultilineCommentEnd(), '/', '\n',
                    ParseableToken("_operations"), '\n']

        self.assertEqual(expected, actual)

    def test_split_verbose_log_statement(self):
        text = '''
logger.info("The value is " + val);
'''
        actual = spl_verbose([ParseableToken(text)])

        expected = ['\n', ParseableToken("logger"), '.', ParseableToken("info"),
                    '(', Quote(), ParseableToken("The"), ParseableToken("value"), ParseableToken("is"), Quote(),
                    '+', ParseableToken('val'), ')', ';', '\n',
                    ]

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
