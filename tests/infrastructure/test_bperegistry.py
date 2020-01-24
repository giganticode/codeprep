# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import os
from unittest.mock import patch

from codeprep.pipeline.bperegistry import get_max_merges, format_available_merge_list_ids, get_min_merges
from codeprep.pipeline.dataset import create_new_id_from


PATH_TO_DATASET_BPE_DIR_STUB = os.path.join('/', 'path', 'to', 'dataset', 'bpe', 'dir')
PATH_TO_DATASET_STUB = os.path.join('/', 'path', 'to', 'dataset')
HLIB_PATH = '/home/hlib/path'


@patch("codeprep.bpepkg.bpe_config.BpeConfig", autospec=True)
def test_with_predefined_id(bpe_config_mock):
    bpe_config_mock.to_suffix.return_value = ''
    assert create_new_id_from(PATH_TO_DATASET_STUB, bpe_config_mock, 'id23') == 'id23'


@patch("codeprep.bpepkg.bpe_config.BpeConfig", autospec=True)
@patch('codeprep.pipeline.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True, return_value={})
def test_no_existing_bpe_codes(mock, bpe_config_mock):
    bpe_config_mock.to_suffix.return_value = ''
    assert create_new_id_from(PATH_TO_DATASET_STUB, bpe_config_mock) == 'dataset'


@patch("codeprep.bpepkg.bpe_config.BpeConfig", autospec=True)
@patch('codeprep.pipeline.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True,
       return_value={'dataset': 10, 'dataset4': 20, 'dataset_3': 30})
def test_ids_for_same_dataset_exist(mock, bpe_config_mock):
    bpe_config_mock.to_suffix.return_value = ''
    assert create_new_id_from(PATH_TO_DATASET_STUB, bpe_config_mock) == 'dataset_4'


@patch("codeprep.bpepkg.bpe_config.BpeConfig", autospec=True)
def test_with_predefined_codes_id(bpe_config_mock):
    bpe_config_mock.to_suffix.return_value = ""
    assert create_new_id_from(HLIB_PATH, bpe_config_mock, 'my-id') == 'my-id'


@patch("codeprep.bpepkg.bpe_config.BpeConfig", autospec=True)
@patch('codeprep.pipeline.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True, return_value="")
def test_simple(mock, bpe_config_mock):
    # given
    bpe_config_mock.to_suffix.return_value = ""

    assert create_new_id_from(HLIB_PATH, bpe_config_mock) == 'path'


@patch("codeprep.bpepkg.bpe_config.BpeConfig", autospec=True)
@patch('codeprep.pipeline.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True,
       return_value={'path': 1000})
def test_same_path_exists(mock, bpe_config_mock):
    # given
    bpe_config_mock.to_suffix.return_value = ""

    assert create_new_id_from(HLIB_PATH, bpe_config_mock) == 'path_1'


@patch("codeprep.bpepkg.bpe_config.BpeConfig", autospec=True)
@patch('codeprep.pipeline.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True,
       return_value={'path': 1000, 'path_1': 2000})
def test_same_path_and_next_one_exist(mock, bpe_config_mock):
    # given
    bpe_config_mock.to_suffix.return_value = ""

    assert create_new_id_from(HLIB_PATH, bpe_config_mock) == 'path_2'


@patch("codeprep.bpepkg.bpe_config.BpeConfig", autospec=True)
@patch('codeprep.pipeline.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True,
       return_value={'path': 1000, 'path_28': 2000})
def test_same_path_and_one_more_exist(mock, bpe_config_mock):
    # given
    bpe_config_mock.to_suffix.return_value = ""

    assert create_new_id_from(HLIB_PATH, bpe_config_mock) == 'path_29'


@patch('codeprep.pipeline.bperegistry.os.walk', return_value=iter([('', [], [])]))
def test_none(mocked_walk):
    assert get_max_merges('.') is None


@patch('codeprep.pipeline.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True, return_value={})
def test_no_available_merge_lists(bpe_registry_mock):
    assert format_available_merge_list_ids() == ""


@patch('codeprep.pipeline.bperegistry._get_all_custom_bpe_codes_and_max_merges', autospec=True,
       return_value={"a": 1000, "b": 500})
def test_simple(mock):
    assert format_available_merge_list_ids() == "a-[1..1000]\nb-[1..500]\n"


@patch('codeprep.pipeline.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=[])
def test_max_no_folders(mock):
    assert get_max_merges(PATH_TO_DATASET_BPE_DIR_STUB) is None


@patch('codeprep.pipeline.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=[])
def test_min_no_folders(mock):
    assert get_min_merges(PATH_TO_DATASET_BPE_DIR_STUB) is None


@patch('codeprep.pipeline.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=['part_vocab'])
def test_max_with_non_number_folder(mock):
    assert get_max_merges(PATH_TO_DATASET_BPE_DIR_STUB) is None


@patch('codeprep.pipeline.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=['part_vocab'])
def test_min_with_non_number_folder(mock):
    assert get_min_merges(PATH_TO_DATASET_BPE_DIR_STUB) is None


@patch('codeprep.pipeline.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=['10', '20'])
def test_max_all_folders_above_limit(mock):
    assert get_max_merges(PATH_TO_DATASET_BPE_DIR_STUB, 5) is None


@patch('codeprep.pipeline.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=['10', '20'])
def test_min_all_folders_below_limit(mock):
    assert get_min_merges(PATH_TO_DATASET_BPE_DIR_STUB) == 10


@patch('codeprep.pipeline.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=['10', 'partvocab'])
def test_max_one_folder_available(mock):
    assert get_max_merges(PATH_TO_DATASET_BPE_DIR_STUB) == 10


@patch('codeprep.pipeline.bperegistry._get_all_bpe_merges_dirs', autospec=True, return_value=['10', 'partvocab'])
def test_min_one_folder_available(mock):
    assert get_max_merges(PATH_TO_DATASET_BPE_DIR_STUB) == 10


@patch('codeprep.pipeline.bperegistry._get_all_bpe_merges_dirs', autospec=True,
       return_value=['10', '20', '15', '30', 'partvocab'])
def test_max_simple(mock):
    assert get_max_merges(PATH_TO_DATASET_BPE_DIR_STUB, 20) == 20


@patch('codeprep.pipeline.bperegistry._get_all_bpe_merges_dirs', autospec=True,
       return_value=['10', '20', '15', '30', 'partvocab'])
def test_min_simple(mock):
    assert get_min_merges(PATH_TO_DATASET_BPE_DIR_STUB, 15) == 15