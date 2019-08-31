import unittest
from unittest import mock

from unittest.mock import Mock

from dataprep.infrastructure.bperegistry import InvalidBpeCodesIdError, get_max_merges, parse_merge_list_id, is_predefined_id, \
    format_available_merge_list_ids, get_min_merges
from dataprep.infrastructure.dataset import create_new_id_from


@mock.patch("dataprep.bpepkg.bpe_config.BpeConfig")
class CreateBpeCodeIdTest(unittest.TestCase):
    def test_with_predefined_id(self, bpe_config_mock):
        bpe_config_mock.to_suffix.return_value = ""
        actual = create_new_id_from('/path/to/dataset', bpe_config_mock, 'id23')
        self.assertEqual('id23', actual)

    @mock.patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges')
    def test_no_existing_bpe_codes(self, mock, bpe_config_mock):
        bpe_config_mock.to_suffix.return_value = ""
        mock.return_value={}
        actual = create_new_id_from('/path/to/dataset', bpe_config_mock)
        self.assertEqual('dataset', actual)

    @mock.patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges')
    def test_ids_for_same_dataset_exist(self, mock, bpe_config_mock):
        bpe_config_mock.to_suffix.return_value = ""
        mock.return_value={'dataset': 10, 'dataset4': 20, 'dataset_3': 30}
        actual = create_new_id_from('/path/to/dataset', bpe_config_mock)
        self.assertEqual('dataset_4', actual)


class ParseBpeCodesIdTest(unittest.TestCase):
    def test_simple(self):
        actual = parse_merge_list_id("python-no-case-1000")
        expected = ('python-no-case', 1000)

        self.assertEqual(expected, actual)

    def test_invalid(self):
        with self.assertRaises(InvalidBpeCodesIdError):
            parse_merge_list_id("python_1000")

    def test_invalid2(self):
        with self.assertRaises(InvalidBpeCodesIdError):
            parse_merge_list_id("python-")


@mock.patch("dataprep.bpepkg.bpe_config.BpeConfig")
class CreateNewIdFromTest(unittest.TestCase):
    def test_with_predefined_codes_id(self, bpe_config_mock):
        bpe_config_mock.to_suffix.return_value = ""
        actual = create_new_id_from('/home/hlib/path', bpe_config_mock, 'my-id')

        self.assertEqual('my-id', actual)

    @mock.patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges')
    def test_simple(self, mock, bpe_config_mock):
        # given
        bpe_config_mock.to_suffix.return_value = ""
        mock.return_value={}

        actual = create_new_id_from('/home/hlib/path', bpe_config_mock)

        self.assertEqual('path', actual)

    @mock.patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges')
    def test_same_path_exists(self, mock, bpe_config_mock):
        # given
        bpe_config_mock.to_suffix.return_value = ""
        mock.return_value={'path': 1000,}

        actual = create_new_id_from('/home/hlib/path', bpe_config_mock)

        self.assertEqual('path_1', actual)

    @mock.patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges')
    def test_same_path_and_next_one_exist(self, mock, bpe_config_mock):
        # given
        bpe_config_mock.to_suffix.return_value = ""
        mock.return_value={'path': 1000, 'path_1': 2000}

        actual = create_new_id_from('/home/hlib/path', bpe_config_mock)

        self.assertEqual('path_2', actual)

    @mock.patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges')
    def test_same_path_and_one_more_exist(self, mock, bpe_config_mock):
        # given
        bpe_config_mock.to_suffix.return_value = ""
        mock.return_value={'path': 1000, 'path_28': 2000}

        actual = create_new_id_from('/home/hlib/path', bpe_config_mock)

        self.assertEqual('path_29', actual)


@mock.patch('dataprep.infrastructure.bperegistry.os')
class GetMaxMergesTest(unittest.TestCase):
    def test_none(self, mocked_os):
        mocked_os.walk = Mock(return_value=iter([('', [],[])]))

        actual = get_max_merges('.')

        self.assertIsNone(actual)


class IsPredefinedIdTest(unittest.TestCase):
    def test_yes(self):
        self.assertTrue(is_predefined_id('1k'))
        self.assertTrue(is_predefined_id('5k'))
        self.assertTrue(is_predefined_id('10k'))

    def test_no(self):
        self.assertFalse(is_predefined_id('abc-10'))
        self.assertFalse(is_predefined_id('abc'))


@mock.patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges')
class FormatAvailableMergeListIds(unittest.TestCase):
    def test_no_available_merge_lists(self, mock):
        mock.return_value = {}
        actual = format_available_merge_list_ids()

        self.assertEqual("", actual)

    def test_simple(self, mock):
        mock.return_value = {"a": 1000, "b": 500}
        actual = format_available_merge_list_ids()

        self.assertEqual("a-[1..1000]\nb-[1..500]\n", actual)


@mock.patch('dataprep.infrastructure.bperegistry._get_all_bpe_merges_dirs')
class GetMinMaxMergesTest(unittest.TestCase):
    def test_max_no_folders(self, mock):
        mock.return_value = []

        self.assertIsNone(get_max_merges('/path/to/dataset/bpe/dir'))

    def test_min_no_folders(self, mock):
        mock.return_value = []

        self.assertIsNone(get_min_merges('/path/to/dataset/bpe/dir'))

    def test_max_with_non_number_folder(self, mock):
        mock.return_value = ['part_vocab']

        self.assertIsNone(get_max_merges('/path/to/dataset/bpe/dir'))

    def test_min_with_non_number_folder(self, mock):
        mock.return_value = ['part_vocab']

        self.assertIsNone(get_min_merges('/path/to/dataset/bpe/dir'))

    def test_max_all_folders_above_limit(self, mock):
        mock.return_value = ['10', '20']

        self.assertIsNone(get_max_merges('/path/to/dataset/bpe/dir', 5))

    def test_min_all_folders_below_limit(self, mock):
        mock.return_value = ['10', '20']

        self.assertIsNone(get_min_merges('/path/to/dataset/bpe/dir', 25))

    def test_max_one_folder_available(self, mock):
        mock.return_value = ['10', 'partvocab']

        self.assertEqual(10, get_max_merges('/path/to/dataset/bpe/dir'))

    def test_min_one_folder_available(self, mock):
        mock.return_value = ['10', 'partvocab']

        self.assertEqual(10, get_min_merges('/path/to/dataset/bpe/dir'))

    def test_max_simple(self, mock):
        mock.return_value = ['10', '20', '15', '30', 'partvocab']

        self.assertEqual(20, get_max_merges('/path/to/dataset/bpe/dir', 20))

    def test_min_simple(self, mock):
        mock.return_value = ['10', '20', '15', '30', 'partvocab']

        self.assertEqual(15, get_min_merges('/path/to/dataset/bpe/dir', 15))


if __name__ == '__main__':
    unittest.main()
