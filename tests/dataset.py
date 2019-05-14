import unittest
from unittest import mock

from dataprep.dataset import create_bpe_codes_id


class DatasetTest(unittest.TestCase):
    def test_create_bpe_codes_id_with_predefined_id(self):
        actual = create_bpe_codes_id('/path/to/dataset', 'id23')
        self.assertEqual('id23', actual)

    @mock.patch('dataprep.dataset.get_all_custom_bpe_codes')
    def test_create_bpe_codes_id_no_existing_bpe_codes(self, mock):
        mock.return_value=[]
        actual = create_bpe_codes_id('/path/to/dataset')
        self.assertEqual('dataset', actual)

    @mock.patch('dataprep.dataset.get_all_custom_bpe_codes')
    def test_create_bpe_codes_id_ids_For_same_dataset_exist(self, mock):
        mock.return_value=['dataset', 'dataset4', 'dataset_3']
        actual = create_bpe_codes_id('/path/to/dataset')
        self.assertEqual('dataset_4', actual)


if __name__ == '__main__':
    unittest.main()
