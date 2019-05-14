import unittest

from dataprep.split.bpe_learn import do_merges


class LearnBpeTest(unittest.TestCase):
    def testDoMergesSimple(self):
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

        expected_merges = [
            ('w', 'o', 20),
            ('wo', 'g', 13),
            ('r', 'd', 10),
            ('wo', 'rd', 7),
            ('b', 'i', 3),
            ('bi', 'rd', 3)
        ]

        self.assertEqual(expected_vocab, actual_vocab)
        self.assertEqual(expected_merges, actual_merges)

    def testDoMergesSameLetter(self):
        input_vocab = {
            "a a a a a": 3,
        }

        actual_vocab, actual_merges = do_merges(input_vocab, 10)

        expected_vocab = {
            "aaaaa": 3,
        }

        expected_merges = [
            ('a', 'a', 12),
            ('aa', 'aa', 3),
            ('aaaa', 'a', 3),
        ]

        self.assertEqual(expected_vocab, actual_vocab)
        self.assertEqual(expected_merges, actual_merges)

    def testDoMergesSameTwoLetters(self):
        input_vocab = {
            "l a l a l a": 3,
        }

        actual_vocab, actual_merges = do_merges(input_vocab, 10)

        expected_vocab = {
            "lalala": 3,
        }

        expected_merges = [
            ('l', 'a', 9),
            ('la', 'la', 6),
            ('lala', 'la', 3),
        ]

        self.assertEqual(expected_vocab, actual_vocab)
        self.assertEqual(expected_merges, actual_merges)


if __name__ == '__main__':
    unittest.main()
