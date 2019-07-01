import unittest

from dataprep.bpepkg.bpe_learn import do_merges
from dataprep.bpepkg.merge import Merge, MergeList


class DoMergesTest(unittest.TestCase):
    def test_simple(self):
        input_vocab = {
            "b i r d": 3,
            "w o r d": 7,
            "w o g": 13
        }

        actual_vocab, actual_merges = do_merges(input_vocab, 10)

        expected_vocab = {
            "bird": 3,
            "word": 7,
            "wog": 13
        }

        expected_merges = MergeList()\
            .append(Merge(('w', 'o'), 20, 0))\
            .append(Merge(('wo', 'g'), 13, 1))\
            .append(Merge(('r', 'd'), 10, 2))\
            .append(Merge(('wo', 'rd'), 7, 3))\
            .append(Merge(('b', 'i'), 3, 4))\
            .append(Merge(('bi', 'rd'), 3, 5))

        self.assertEqual(expected_vocab, actual_vocab)
        self.assertEqual(expected_merges, actual_merges)

    def test_same_letter(self):
        input_vocab = {
            "a a a a a": 3,
        }

        actual_vocab, actual_merges = do_merges(input_vocab, 10)

        expected_vocab = {
            "aaaaa": 3,
        }

        expected_merges = MergeList().append(Merge(('a', 'a'), 12, 0))\
            .append(Merge(('aa', 'aa'), 3, 1))\
            .append(Merge(('aaaa', 'a'), 3, 2))

        self.assertEqual(expected_vocab, actual_vocab)
        self.assertEqual(expected_merges, actual_merges)

    def test_same_two_letters(self):
        input_vocab = {
            "l a l a l a": 3,
        }

        actual_vocab, actual_merges = do_merges(input_vocab, 10)

        expected_vocab = {
            "lalala": 3,
        }

        expected_merges = MergeList()\
            .append(Merge(('l', 'a'), 9, 0))\
            .append(Merge(('la', 'la'), 6, 1))\
            .append(Merge(('lala', 'la'), 3, 2))

        self.assertEqual(expected_vocab, actual_vocab)
        self.assertEqual(expected_merges, actual_merges)


if __name__ == '__main__':
    unittest.main()
