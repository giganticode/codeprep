import unittest

from dataprep.split.full_word_iterator import FullWordIterator
from dataprep.parse.model.placeholders import placeholders

def iter_to_int_list(it):
    return [w for w in it]


class FullwordIteratorTest(unittest.TestCase):
    def test1(self):
        input_str = ['}', '}',
                     placeholders['word_start'],
                     placeholders['capital'],
                     'a',
                     'a',
                     placeholders['word_end'],
                     '}',
                     placeholders['capitals']]

        full_word_indexes = [(0, 1), (1, 2), (2, 7), (7, 8)]

        expected = [(input_str[range[0]: range[1]], range) for range in full_word_indexes]

        it = FullWordIterator(input_str)

        actual = iter_to_int_list(it)
        self.assertEqual(expected, actual)

        it.add_data(['a', placeholders['word_start'], '_'])
        actual = iter_to_int_list(it)
        self.assertEqual(
            [([placeholders['capitals'], 'a'], (0, 2))], actual
        )

        it.add_data(['_', placeholders['word_end']])
        actual = iter_to_int_list(it)
        self.assertEqual(
            [([placeholders['word_start'], '_', '_', placeholders['word_end']], (0, 4))], actual
        )

    def test_empty(self):
        it = FullWordIterator([])

        actual = [i for i in it]
        self.assertEqual([], actual)

    def test_not_full_word(self):
        targets_str = [placeholders['capitals']]

        it = FullWordIterator(targets_str)

        actual = [i for i in it]
        self.assertEqual([], actual)


if __name__ == '__main__':
    unittest.main()
