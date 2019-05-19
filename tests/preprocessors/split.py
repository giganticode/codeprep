import unittest

from dataprep.model.chars import Quote
from dataprep.model.containers import StringLiteral, SplitContainer
from dataprep.model.core import ParseableToken
from dataprep.model.word import Underscore, Word
from dataprep.preprocessors.split import simple_split


class SplitTest(unittest.TestCase):

    def test_with_numbers_split(self):
        token = [StringLiteral([Quote(), ":", ParseableToken("_test_my123GmyClass_"), Quote()])]
        actual = simple_split(token)

        expected = [StringLiteral([Quote(), ":", SplitContainer([
            Underscore(),
            Word.from_("test"),
            Underscore(),
            Word.from_("my"),
            Word.from_("123"),
            Word.from_("Gmy"),
            Word.from_("Class"),
            Underscore()
        ]), Quote()])]
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
