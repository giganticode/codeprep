import unittest

from dataprep.util import merge_dicts_


class UtilTest(unittest.TestCase):
    def test_merge_dicts(self):
        dict1 = {"a": 3, "b": 4}
        dict2 = {"b": 5, "c": 6}

        merge_dicts_(dict1, dict2)

        expected = {"a": 3, "b": 9, "c": 6}

        self.assertEqual(expected, dict1)


if __name__ == '__main__':
    unittest.main()
