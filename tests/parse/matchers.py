import unittest

from dataprep.parse.matchers import split_string_tokens


class MatchersTest(unittest.TestCase):
    def test_split_string_tokens(self):
        actual = split_string_tokens("123\nAb2cd34Ef000GG j_89_J")
        expected = ["123", "\n", "Ab2cd34Ef000GG", "j_89_J"]

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()