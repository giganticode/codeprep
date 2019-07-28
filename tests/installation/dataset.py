import os
import unittest
from unittest import mock

from dataprep.config import USER_CONFIG_DIR, VOCAB_DIR, BPE_DIR, USER_CACHE_DIR

from dataprep.bpepkg.bpe_config import BpeConfig, BpeParam

from dataprep.infrastructure.bperegistry import CustomBpeConfig
from dataprep.infrastructure.dataset import Dataset, SubDataset, normalize_extension_string
from dataprep.fileutils import has_one_of_extensions
from dataprep.prepconfig import PrepConfig, PrepParam


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


@mock.patch('os.path.exists')
@mock.patch('dataprep.infrastructure.dataset.get_timestamp')
@mock.patch('dataprep.infrastructure.dataset.DEFAULT_PARSED_DATASETS_DIR', '/parsed/dataset')
@mock.patch('dataprep.infrastructure.dataset.DEFAULT_PREP_DATASETS_DIR', '/prep/dataset')
class CreateTest(unittest.TestCase):
    def test_non_bpe_split(self, get_timestamp_mock, os_exists_mock):
        os_exists_mock.return_value = True
        get_timestamp_mock.return_value = "01_01_01"
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM: 'c',
            PrepParam.STR: '1',
            PrepParam.SPLIT: '0',
            PrepParam.TABS_NEWLINES: 's',
            PrepParam.CASE: 'u'
        })

        actual = Dataset.create('/path/to/dataset', prep_config, None, None)

        self.assertEqual('/path/to/dataset', actual._path)
        self.assertEqual(prep_config, actual._prep_config)
        self.assertEqual(None, actual._normalized_extension_list)
        self.assertEqual(None, actual._custom_bpe_config)
        self.assertEqual(None, actual._bpe_config)
        self.assertEqual('01_01_01', actual._dataset_last_modified)

        self.assertEqual(SubDataset(actual, '/path/to/dataset', ''), actual._original)
        self.assertEqual(SubDataset(actual, '/parsed/dataset/dataset_01_01_01', '.parsed'), actual._parsed)
        self.assertEqual(SubDataset(actual, '/prep/dataset/dataset_01_01_01_-_uc10su', '.prep'), actual._preprocessed)

    def test_non_bpe_split_with_one_extension(self, get_timestamp_mock, os_exists_mock):
        os_exists_mock.return_value = True
        get_timestamp_mock.return_value = "01_01_01"
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM: 'c',
            PrepParam.STR: '1',
            PrepParam.SPLIT: '0',
            PrepParam.TABS_NEWLINES: 's',
            PrepParam.CASE: 'u'
        })

        actual = Dataset.create('/path/to/dataset', prep_config, "java", None)

        self.assertEqual('/path/to/dataset', actual._path)
        self.assertEqual(prep_config, actual._prep_config)
        self.assertEqual(['java'], actual._normalized_extension_list)
        self.assertEqual(None, actual._custom_bpe_config)
        self.assertEqual(None, actual._bpe_config)
        self.assertEqual('01_01_01', actual._dataset_last_modified)

        self.assertEqual(SubDataset(actual, '/path/to/dataset', ''), actual._original)
        self.assertEqual(SubDataset(actual, '/parsed/dataset/dataset_01_01_01_java', '.parsed'), actual._parsed)
        self.assertEqual(SubDataset(actual, '/prep/dataset/dataset_01_01_01_java_-_uc10su', '.prep'), actual._preprocessed)

    def test_all_custom(self, get_timestamp_mock, os_exists_mock):
        os_exists_mock.return_value = True
        get_timestamp_mock.return_value = "01_01_01"
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM: 'c',
            PrepParam.STR: '1',
            PrepParam.SPLIT: '0',
            PrepParam.TABS_NEWLINES: 's',
            PrepParam.CASE: 'u'
        })
        bpe_config = BpeConfig({
            BpeParam.CASE: 'no',
            BpeParam.WORD_END: False,
            BpeParam.BASE: "code",
            BpeParam.UNICODE: "no",
        })

        custom_bpe_config = CustomBpeConfig("id", 1000, "/codes/file", "/cache/file")
        actual = Dataset.create('/path/to/dataset', prep_config, "c|java", custom_bpe_config,
                                bpe_config, overriden_path_to_prep_dataset="/path/overridden")

        self.assertEqual('/path/to/dataset', actual._path)
        self.assertEqual(prep_config, actual._prep_config)
        self.assertEqual(['c', 'java'], actual._normalized_extension_list)
        self.assertEqual(custom_bpe_config, actual._custom_bpe_config)
        self.assertEqual(bpe_config, actual._bpe_config)
        self.assertEqual('01_01_01', actual._dataset_last_modified)

        self.assertEqual(SubDataset(actual, '/path/to/dataset', ''), actual.original)
        self.assertEqual(SubDataset(actual, '/parsed/dataset/dataset_01_01_01_c_java', '.parsed'), actual.parsed)
        self.assertEqual(SubDataset(actual, '/path/overridden/dataset_01_01_01_c_java_-_uc10su_id-1000_-_prep', '.prep'), actual.preprocessed)
        self.assertEqual(os.path.join(USER_CONFIG_DIR, VOCAB_DIR , 'dataset_01_01_01_c_java_-_Uc11sl'), actual.base_bpe_vocab_path)
        self.assertEqual(os.path.join(USER_CONFIG_DIR, BPE_DIR , 'dataset_01_01_01_c_java_-_nocase_nounicode'), actual.bpe_path)
        self.assertEqual(os.path.join(USER_CACHE_DIR, 'file_lists' , 'dataset_01_01_01_c_java'), actual.path_to_file_list_folder)
        self.assertEqual(os.path.join(USER_CONFIG_DIR, VOCAB_DIR , 'dataset_01_01_01_c_java_-_uc10su_id-1000'), actual.vocab_path)


class NormalizeExtensionStringTest(unittest.TestCase):
    def test_simple(self):
        actual = normalize_extension_string("java|c|python")
        self.assertEqual(['c', 'java', 'python'], actual)

    def test_single(self):
        actual = normalize_extension_string("java")
        self.assertEqual(['java'], actual)

    def test_repetitive(self):
        actual = normalize_extension_string("java|c|java")
        self.assertEqual(['c', 'java'], actual)

    def test_none(self):
        actual = normalize_extension_string(None)
        self.assertIsNone(actual)


if __name__ == '__main__':
    unittest.main()
