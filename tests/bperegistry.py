import unittest
from unittest import mock

from dataprep.dataset import create_new_id_from


class BpeRegistryTest(unittest.TestCase):
    def test_create_bpe_codes_id_with_predefined_id(self):
        actual = create_new_id_from('/path/to/dataset', 'id23')
        self.assertEqual('id23', actual)

    @mock.patch('dataprep.bperegistry.get_all_custom_bpe_codes_with_max_merges')
    def test_create_bpe_codes_id_no_existing_bpe_codes(self, mock):
        mock.return_value={}
        actual = create_new_id_from('/path/to/dataset')
        self.assertEqual('dataset', actual)

    @mock.patch('dataprep.bperegistry.get_all_custom_bpe_codes_with_max_merges')
    def test_create_bpe_codes_id_ids_For_same_dataset_exist(self, mock):
        mock.return_value={'dataset': 10, 'dataset4': 20, 'dataset_3': 30}
        actual = create_new_id_from('/path/to/dataset')
        self.assertEqual('dataset_4', actual)


if __name__ == '__main__':
    unittest.main()
