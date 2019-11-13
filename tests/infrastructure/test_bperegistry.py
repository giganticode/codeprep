from unittest.mock import patch

from dataprep.infrastructure.bperegistry import get_max_merges, format_available_merge_list_ids, get_min_merges
from dataprep.infrastructure.dataset import create_new_id_from


@patch("dataprep.bpepkg.bpe_config.BpeConfig", autospec=True)
def test_with_predefined_id(bpe_config_mock):
    bpe_config_mock.to_suffix.return_value = ''
    assert create_new_id_from('/path/to/dataset', bpe_config_mock, 'id23') == 'id23'


@patch("dataprep.bpepkg.bpe_config.BpeConfig", autospec=True)
@patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True, return_value={})
def test_no_existing_bpe_codes(mock, bpe_config_mock):
    bpe_config_mock.to_suffix.return_value = ''
    assert create_new_id_from('/path/to/dataset', bpe_config_mock) == 'dataset'


@patch("dataprep.bpepkg.bpe_config.BpeConfig", autospec=True)
@patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True,
       return_value={'dataset': 10, 'dataset4': 20, 'dataset_3': 30})
def test_ids_for_same_dataset_exist(mock, bpe_config_mock):
    bpe_config_mock.to_suffix.return_value = ''
    assert create_new_id_from('/path/to/dataset', bpe_config_mock) == 'dataset_4'


@patch("dataprep.bpepkg.bpe_config.BpeConfig", autospec=True)
def test_with_predefined_codes_id(bpe_config_mock):
    bpe_config_mock.to_suffix.return_value = ""
    assert create_new_id_from('/home/hlib/path', bpe_config_mock, 'my-id') == 'my-id'


@patch("dataprep.bpepkg.bpe_config.BpeConfig", autospec=True)
@patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True, return_value="")
def test_simple(mock, bpe_config_mock):
    # given
    bpe_config_mock.to_suffix.return_value = ""

    assert create_new_id_from('/home/hlib/path', bpe_config_mock) == 'path'


@patch("dataprep.bpepkg.bpe_config.BpeConfig", autospec=True)
@patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True,
       return_value={'path': 1000})
def test_same_path_exists(mock, bpe_config_mock):
    # given
    bpe_config_mock.to_suffix.return_value = ""

    assert create_new_id_from('/home/hlib/path', bpe_config_mock) == 'path_1'


@patch("dataprep.bpepkg.bpe_config.BpeConfig", autospec=True)
@patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True,
       return_value={'path': 1000, 'path_1': 2000})
def test_same_path_and_next_one_exist(mock, bpe_config_mock):
    # given
    bpe_config_mock.to_suffix.return_value = ""

    assert create_new_id_from('/home/hlib/path', bpe_config_mock) == 'path_2'


@patch("dataprep.bpepkg.bpe_config.BpeConfig", autospec=True)
@patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True,
       return_value={'path': 1000, 'path_28': 2000})
def test_same_path_and_one_more_exist(mock, bpe_config_mock):
    # given
    bpe_config_mock.to_suffix.return_value = ""

    assert create_new_id_from('/home/hlib/path', bpe_config_mock) == 'path_29'


@patch('dataprep.infrastructure.bperegistry.os.walk', return_value=iter([('', [], [])]))
def test_none(mocked_walk):
    assert get_max_merges('.') is None


@patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True, return_value={})
def test_no_available_merge_lists(bpe_registry_mock):
    assert format_available_merge_list_ids() == ""


@patch('dataprep.infrastructure.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True,
       return_value={"a": 1000, "b": 500})
def test_simple(mock):
    assert format_available_merge_list_ids() == "a-[1..1000]\nb-[1..500]\n"


@patch('dataprep.infrastructure.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=[])
def test_max_no_folders(mock):
    assert get_max_merges('/path/to/dataset/bpe/dir') is None


@patch('dataprep.infrastructure.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=[])
def test_min_no_folders(mock):
    assert get_min_merges('/path/to/dataset/bpe/dir') is None


@patch('dataprep.infrastructure.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=['part_vocab'])
def test_max_with_non_number_folder(mock):
    assert get_max_merges('/path/to/dataset/bpe/dir') is None


@patch('dataprep.infrastructure.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=['part_vocab'])
def test_min_with_non_number_folder(mock):
    assert get_min_merges('/path/to/dataset/bpe/dir') is None


@patch('dataprep.infrastructure.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=['10', '20'])
def test_max_all_folders_above_limit(mock):
    assert get_max_merges('/path/to/dataset/bpe/dir', 5) is None


@patch('dataprep.infrastructure.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=['10', '20'])
def test_min_all_folders_below_limit(mock):
    assert get_min_merges('/path/to/dataset/bpe/dir') == 10


@patch('dataprep.infrastructure.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=['10', 'partvocab'])
def test_max_one_folder_available(mock):
    assert get_max_merges('/path/to/dataset/bpe/dir') == 10


@patch('dataprep.infrastructure.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=['10', 'partvocab'])
def test_min_one_folder_available(mock):
    assert get_max_merges('/path/to/dataset/bpe/dir') == 10


@patch('dataprep.infrastructure.bperegistry._get_all_bpe_merges_dirs', autospec=True,
       return_value=['10', '20', '15', '30', 'partvocab'])
def test_max_simple(mock):
    assert get_max_merges('/path/to/dataset/bpe/dir', 20) == 20


@patch('dataprep.infrastructure.bperegistry._get_all_bpe_merges_dirs', autospec=True,
       return_value=['10', '20', '15', '30', 'partvocab'])
def test_min_simple(mock):
    assert get_min_merges('/path/to/dataset/bpe/dir', 15) == 15