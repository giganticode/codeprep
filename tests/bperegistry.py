import unittest
from unittest import mock
from unittest.mock import Mock

from dataprep.bperegistry import parse_bpe_codes_id, InvalidBpeCodesIdError, get_max_merges
from dataprep.dataset import create_new_id_from


class CreateBpeCodeIdTest(unittest.TestCase):
    def test_with_predefined_id(self):
        actual = create_new_id_from('/path/to/dataset', 'id23')
        self.assertEqual('id23', actual)

    @mock.patch('dataprep.bperegistry.get_all_custom_bpe_codes_with_max_merges')
    def test_no_existing_bpe_codes(self, mock):
        mock.return_value={}
        actual = create_new_id_from('/path/to/dataset')
        self.assertEqual('dataset', actual)

    @mock.patch('dataprep.bperegistry.get_all_custom_bpe_codes_with_max_merges')
    def test_ids_for_same_dataset_exist(self, mock):
        mock.return_value={'dataset': 10, 'dataset4': 20, 'dataset_3': 30}
        actual = create_new_id_from('/path/to/dataset')
        self.assertEqual('dataset_4', actual)


class ParseBpeCodesIdTest(unittest.TestCase):
    def test_simple(self):
        actual = parse_bpe_codes_id("python-no-case-1000")
        expected = ('python-no-case', 1000)

        self.assertEqual(expected, actual)

    def test_invalid(self):
        with self.assertRaises(InvalidBpeCodesIdError):
            parse_bpe_codes_id("python_1000")

    def test_invalid2(self):
        with self.assertRaises(InvalidBpeCodesIdError):
            parse_bpe_codes_id("python-")


class CreateNewIdFromTest(unittest.TestCase):
    def test_with_predefined_codes_id(self):
        actual = create_new_id_from('/home/hlib/path', 'my-id')

        self.assertEqual('my-id', actual)

    @mock.patch('dataprep.bperegistry.get_all_custom_bpe_codes_with_max_merges')
    def test_simple(self, mock):
        # given
        mock.return_value={}

        actual = create_new_id_from('/home/hlib/path')

        self.assertEqual('path', actual)

    @mock.patch('dataprep.bperegistry.get_all_custom_bpe_codes_with_max_merges')
    def test_same_path_exists(self, mock):
        # given
        mock.return_value={'path': 1000,}

        actual = create_new_id_from('/home/hlib/path')

        self.assertEqual('path_1', actual)

    @mock.patch('dataprep.bperegistry.get_all_custom_bpe_codes_with_max_merges')
    def test_same_path_and_next_one_exist(self, mock):
        # given
        mock.return_value={'path': 1000, 'path_1': 2000}

        actual = create_new_id_from('/home/hlib/path')

        self.assertEqual('path_2', actual)

    @mock.patch('dataprep.bperegistry.get_all_custom_bpe_codes_with_max_merges')
    def test_same_path_and_one_more_exist(self, mock):
        # given
        mock.return_value={'path': 1000, 'path_28': 2000}

        actual = create_new_id_from('/home/hlib/path')

        self.assertEqual('path_29', actual)


@mock.patch('dataprep.bperegistry.os')
class GetMaxMergesTest(unittest.TestCase):
    def test_none(self, mocked_os):
        mocked_os.walk = Mock(return_value=iter([('', [],[])]))

        actual = get_max_merges('.')

        self.assertIsNone(actual)


if __name__ == '__main__':
    unittest.main()
