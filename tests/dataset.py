import unittest

from dataprep.dataset import has_one_of_extensions


class HasOneOfExtensionsTest(unittest.TestCase):
    def test_simple(self):
        self.assertTrue(has_one_of_extensions(b'/home/abc.java', [b'java', b'c']))

    def test_no_extension_in_the_list(self):
        self.assertFalse(has_one_of_extensions(b'/home/abc.py', [b'java', b'c']))

    def test_end_of_extension_in_the_list(self):
        self.assertFalse(has_one_of_extensions(b'/home/abc.dtc', [b'java', b'c']))

    def test_double_extension(self):
        self.assertTrue(has_one_of_extensions(b'/home/abc.f.java.prep', [b'java.prep', b'c']))

    def test_end_of_double_extension(self):
        self.assertFalse(has_one_of_extensions(b'/home/abc.f.java.prep', [b'a.prep', b'c']))


if __name__ == '__main__':
    unittest.main()
