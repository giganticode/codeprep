import unittest
from unittest import mock

from dataprep.split import bpe_learn
from dataprep.split.bpe_config import BpeConfigNotSupported, BpeConfig, BpeParam
from dataprep.split.bpe_learn import do_merges


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

    def test_same_letter(self):
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

    def test_same_two_letters(self):
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


@mock.patch('dataprep.split.bpe_learn.Dataset')
class RunTest(unittest.TestCase):
    def test_prefix_case(self, mocked_dataset):
        bpe_config = BpeConfig({
            BpeParam.BASE: 'code',
            BpeParam.WORD_END: False,
            BpeParam.UNICODE: 'yes',
            BpeParam.CASE: 'prefix'
        })
        with self.assertRaises(BpeConfigNotSupported):
            bpe_learn.run(mocked_dataset, 1, bpe_config)

    def test_word_end(self, mocked_dataset):
        bpe_config = BpeConfig({
            BpeParam.BASE: 'code',
            BpeParam.WORD_END: True,
            BpeParam.UNICODE: 'yes',
            BpeParam.CASE: 'no'
        })
        with self.assertRaises(BpeConfigNotSupported):
            bpe_learn.run(mocked_dataset, 1, bpe_config)

    def test_bytes_bpe(self, mocked_dataset):
        bpe_config = BpeConfig({
            BpeParam.BASE: 'code',
            BpeParam.WORD_END: False,
            BpeParam.UNICODE: 'bytes',
            BpeParam.CASE: 'no'
        })
        with self.assertRaises(BpeConfigNotSupported):
            bpe_learn.run(mocked_dataset, 1, bpe_config)

if __name__ == '__main__':
    unittest.main()
