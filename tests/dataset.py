import unittest
from unittest import mock

from dataprep.dataset import Dataset, SubDataset
from dataprep.prepconfig import PrepConfig, PrepParam


@mock.patch('os.path.exists')
@mock.patch('dataprep.dataset.get_timestamp')
@mock.patch('dataprep.dataset.DEFAULT_PARSED_DATASETS_DIR', '/parsed/dataset')
@mock.patch('dataprep.dataset.DEFAULT_PREP_DATASETS_DIR', '/prep/dataset')
class CreateTest(unittest.TestCase):
    def test_simple(self, get_timestamp_mock, os_exists_mock):
        os_exists_mock.return_value = True
        get_timestamp_mock.return_value = "01_01_01"
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 0,
            PrepParam.CAPS: 0
        })

        actual = Dataset.create('/path/to/dataset', prep_config, None, None)

        self.assertEqual('/path/to/dataset', actual._path)
        self.assertEqual(prep_config, actual._prep_config)
        self.assertEqual(None, actual._extension)
        self.assertEqual(None, actual._bpe_config)
        self.assertEqual('01_01_01', actual._dataset_last_modified)

        self.assertEqual(SubDataset(actual, '/path/to/dataset', ''), actual._original)
        self.assertEqual(SubDataset(actual, '/parsed/dataset/dataset_01_01_01', '.parsed'), actual._parsed)
        self.assertEqual(SubDataset(actual, '/prep/dataset/dataset_01_01_01_00000', '.prep'), actual._preprocessed)

    @mock.patch("dataprep.split.bpe_config.BpeConfig")
    def test_simple2(self, mocked_bpe_config, get_timestamp_mock, os_exists_mock):
        os_exists_mock.return_value = True
        get_timestamp_mock.return_value = "01_01_01"
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 0,
            PrepParam.CAPS: 0
        })

        actual = Dataset.create('/path/to/dataset', prep_config, "c",
                                mocked_bpe_config, overriden_path_to_prep_dataset="/path/overridden")

        self.assertEqual('/path/to/dataset', actual._path)
        self.assertEqual(prep_config, actual._prep_config)
        self.assertEqual("c", actual._extension)
        self.assertEqual(mocked_bpe_config, actual._bpe_config)
        self.assertEqual('01_01_01', actual._dataset_last_modified)

        self.assertEqual(SubDataset(actual, '/path/to/dataset', ''), actual._original)
        self.assertEqual(SubDataset(actual, '/parsed/dataset/dataset_01_01_01', '.parsed'), actual._parsed)
        self.assertEqual(SubDataset(actual, '/path/overridden/dataset_01_01_01_00000_prep', '.prep'), actual._preprocessed)


if __name__ == '__main__':
    unittest.main()