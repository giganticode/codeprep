import unittest
from unittest import mock

from unittest.mock import patch, MagicMock

from dataprep.bpepkg import merge
from dataprep.bpepkg.merge import MergeList, Merge


@patch('dataprep.bpepkg.merge.open')
class ReadMergesTest(unittest.TestCase):
    def test_simple(self, open_mock):
        open_mock.return_value = MagicMock(spec=['__enter__', '__exit__'])
        handle = open_mock.return_value.__enter__.return_value
        handle.__iter__.return_value = iter(['a b 67', 'b c 34', 'c d 94'])

        actual = merge.read_merges('file', 2)
        expected = MergeList().append(Merge(('a', 'b'), 67, 0)).append(Merge(('b', 'c'), 34, 1))

        self.assertEqual(expected, actual)

    def test_wrong_delimiter(self, open_mock):
        with self.assertRaises(ValueError):
            open_mock.return_value = MagicMock(spec=['__enter__', '__exit__'])
            handle = open_mock.return_value.__enter__.return_value
            handle.__iter__.return_value = iter(['a\tb\t67'])

            merge.read_merges('file')


@patch('dataprep.bpepkg.merge.open')
class WriteMergesTest(unittest.TestCase):
    def test_simple(self, open_mock):
        open_mock.return_value = MagicMock(spec=['__enter__', '__exit__'])
        handle = open_mock.return_value.__enter__.return_value

        merges = MergeList().append(Merge(('a', 'b'), 67, 0)).append(Merge(('b', 'c'), 34, 1))
        merge.dump_merges(merges, 'file')

        handle.write.assert_has_calls([
            mock.call('a b 67\n'),
            mock.call('b c 34\n')
        ])


class MergeTest(unittest.TestCase):
    def test_merge_as_key(self):
        merge1 = Merge(('a', 'b'), 34, 0)
        merge2 = Merge(('a', 'b'), 34, 0)
        map = {merge1: 3}

        self.assertEqual(3, map[merge2])


class MergeListTest(unittest.TestCase):
    def test_append_wrong_priority(self):
        with self.assertRaises(ValueError):
            merges = MergeList()
            merges.append(Merge(('a', 'b'), 34, 3))

    def test_get_priority(self):
        merges = MergeList()
        merges.append(Merge(('a', 'b'), 34, 0)).append(Merge(('b', 'c'), 44))
        actual = merges.get_priority(('b', 'c'))

        self.assertEqual(1, actual)


class MergeListInclusionTest(unittest.TestCase):
    def test_present(self):
        merges = MergeList()
        merges.append(Merge(('a', 'b'), 34, 0)).append(Merge(('b', 'c'), 44, 1))
        self.assertTrue(('a', 'b') in merges)

    def test_absent(self):
        merges = MergeList()
        merges.append(Merge(('a', 'b'), 34, 0)).append(Merge(('b', 'c'), 44, 1))
        self.assertFalse(('g', 'r') in merges)


class MergeListIndexTest(unittest.TestCase):
    def test_simple(self):
        merges = MergeList()
        merges.append(Merge(('a', 'b'), 34, 0)).append(Merge(('b', 'c'), 44))

        actual = merges[1]
        expected = (Merge(('b', 'c'), 44, 1))

        self.assertEqual(expected, actual)

    def test_out_of_range(self):
        with self.assertRaises(IndexError):
            merges = MergeList()
            merges.append(Merge(('a', 'b'), 34, 0)).append(Merge(('b', 'c'), 44, 1))

            actual = merges[2]

    def test_negative(self):
        merges = MergeList()
        merges.append(Merge(('a', 'b'), 34, 0)).append(Merge(('b', 'c'), 44))

        actual = merges[-1]
        expected = (Merge(('b', 'c'), 44, 1))

        self.assertEqual(expected, actual)

    def test_range_with_negative(self):
        merges = MergeList()
        merges.append(Merge(('a', 'b'), 34)).append(Merge(('b', 'c'), 44))

        actual = merges[0:-1]
        expected = [Merge(('a', 'b'), 34, 0)]

        self.assertEqual(expected, actual)


class MergeListPlusOperationTest(unittest.TestCase):
    def test_simple(self):
        merges1 = MergeList()
        merges1.append(Merge(('a', 'b'), 34, 0)).append(Merge(('b', 'c'), 44, 1))

        merges2 = MergeList()
        merges2.append(Merge(('c', 'd'), 64, 0)).append(Merge(('d', 'e'), 84, 1))

        expected = MergeList()
        expected.append(Merge(('a', 'b'), 34, 0)).append(Merge(('b', 'c'), 44, 1))\
            .append(Merge(('c', 'd'), 64, 2)).append(Merge(('d', 'e'), 84, 3))

        actual = merges1 + merges2

        self.assertEqual(expected, actual)

    def test_add_wrong_type(self):
        with self.assertRaises(TypeError):
            merges = MergeList()
            merges + [(('d', 'e'), 84, 1)]


class MergeListLenTest(unittest.TestCase):
    def test_simple(self):
        merges = MergeList()
        merges.append(Merge(('a', 'b'), 34, 0)).append(Merge(('b', 'c'), 44, 1))

        actual = len(merges)

        self.assertEqual(2, actual)


class MergeListIteratorTest(unittest.TestCase):
    def test_simple(self):
        merges = MergeList()
        merges.append(Merge(('a', 'b'), 34, 0)).append(Merge(('b', 'c'), 44, 1))

        for idx, merge in enumerate(merges):
            self.assertEqual(merges[idx], merge)


if __name__ == '__main__':
    unittest.main()