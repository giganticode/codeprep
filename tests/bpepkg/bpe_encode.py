import os
import unittest

from dataprep.bpepkg.bpe_encode import encode_word
from dataprep.bpepkg.merge import read_merges
from dataprep.config import DEFAULT_BPE_DIR

merge_file = os.path.join(DEFAULT_BPE_DIR, '10k', 'merges.txt')
merges = read_merges(merge_file, 10000)

class BpeEncodeTest(unittest.TestCase):
    def test_encode_simple(self):
        actual = encode_word('this@@is_all_one_String@', merges)
        expected = ['this', '@@', 'is_', 'all', '_', 'one', '_', 'String@']
        self.assertEqual(expected, actual)

    def test_same_letter(self):
        actual = encode_word('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@', merges)
        expected = ['aaaaaaaa', 'aaaaaaaa', 'aaaaaaaa', 'aaaaaaaa', 'aaaa', 'a', 'a@']
        self.assertEqual(expected, actual)

    def test_same_letter_pair(self):
        actual = encode_word('erererererererererererer@', merges)
        expected = ['er', 'er', 'er', 'er', 'er', 'er', 'er', 'er', 'er', 'er', 'er', 'er@']
        self.assertEqual(expected, actual)

    def test_one_letter(self):
        actual = encode_word('@', merges)
        expected = ['@']
        self.assertEqual(expected, actual)

    def test_empty(self):
        actual = encode_word('', merges)
        expected = ['']
        self.assertEqual(expected, actual)

    def test_full_merge(self):
        actual = encode_word('split@', merges)
        expected = ['split@']
        self.assertEqual(expected, actual)

    def test_merge_order(self):
        actual = encode_word('aaa', merges)
        expected = ['aa', 'a']
        self.assertEqual(expected, actual)

    def test_larger_string(self):
        actual = encode_word('this\xa0is@@a@@@@bit@@@@larger\xa0stringwith\xa0some@@unicode@@possibly\xf7@', merges)
        expected = ['this',
 '\xa0',
 'is',
 '@@',
 'a',
 '@@',
 '@@',
 'bit',
 '@@',
 '@@',
 'l',
 'arg',
 'er',
 '\xa0',
 'string',
 'with',
 '\xa0',
 's',
 'ome',
 '@@',
 'unic',
 'ode',
 '@@',
 'pos',
 'si',
 'b',
 'ly',
 '÷',
 '@']
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()