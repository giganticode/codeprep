import unittest

from dataprep.parse.matchers import split_string
from dataprep.parse.model.containers import SplitContainer
from dataprep.parse.model.whitespace import NewLine
from dataprep.parse.model.word import Word, Underscore


class SplitStringTest(unittest.TestCase):
    def test_simple(self):
        actual = split_string("123\nAb2cd34Ef000GG j_89_J")

        expected = [SplitContainer.from_single_token('123'),
                    NewLine(),
                    SplitContainer([Word.from_('Ab'), Word.from_('2'), Word.from_('cd'),
                                    Word.from_('34'), Word.from_('Ef'), Word.from_('000'), Word.from_('GG')]),
                    SplitContainer([Word.from_('j'), Underscore(), Word.from_('89'), Underscore(), Word.from_('J')])]

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
