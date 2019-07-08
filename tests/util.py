import unittest

from dataprep.util import merge_dicts_, groupify


class UtilTest(unittest.TestCase):
    def test_merge_dicts(self):
        dict1 = {"a": 3, "b": 4}
        dict2 = {"b": 5, "c": 6}

        merge_dicts_(dict1, dict2)

        expected = {"a": 3, "b": 9, "c": 6}

        self.assertEqual(expected, dict1)


class GroupifyTest(unittest.TestCase):
    def test_simple(self):
        lst = [0, 1, 2, 3, 4, 5, 6]

        actual = groupify(lst, 3)

        self.assertEqual([[0, 3, 6], [1, 4], [2, 5]], actual)

    def test_more_chunks(self):
        lst = [0, 1, 2, 3, 4, 5, 6]

        actual = groupify(lst, 300)

        self.assertEqual([[0], [1], [2], [3], [4], [5], [6]], actual)

    def test_empty(self):
        lst = []

        actual = groupify(lst, 300)

        self.assertEqual([], actual)

    def test_huge_list(self):
        lst = list(range(100 * 1000 + 17))

        actual = groupify(lst, 100)

        self.assertEqual(1001, len(actual[0]))
        self.assertEqual(1000, len(actual[17]))


if __name__ == '__main__':
    unittest.main()
