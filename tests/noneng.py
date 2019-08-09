import unittest

from dataprep.noneng import replace_non_ascii_seqs


class ReplaceNonAsciiSeqsTest(unittest.TestCase):
    def test_bad_placeholder(self):
        with self.assertRaises(ValueError):
            replace_non_ascii_seqs("any_string", "\xf7\xa0")

    def test_empty(self):
        self.assertEqual("", replace_non_ascii_seqs("","\xf7"))

    def test_single_non_ascii(self):
        self.assertEqual("\xf7", replace_non_ascii_seqs("Ü", "\xf7")) 

    def test_multiple_non_ascii(self):
        self.assertEqual("\xf7", replace_non_ascii_seqs("Üüø", "\xf7"))

    def test_all_ascii(self):
        self.assertEqual("abcd", replace_non_ascii_seqs("abcd", "\xf7"))

    def test_ascii_non_ascii_alternate(self):
        self.assertEqual("a\xf7b\xf7cd\xf7", replace_non_ascii_seqs("aæbñńcdú", "\xf7"))


if __name__ == '__main__':
    unittest.main()
