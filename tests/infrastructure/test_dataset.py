# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import os
from unittest import mock

from codeprep.bpepkg.bpe_config import BpeConfig, BpeParam
from codeprep.config import USER_CONFIG_DIR, VOCAB_DIR, BPE_DIR, USER_CACHE_DIR
from codeprep.pipeline.bperegistry import CustomBpeConfig
from codeprep.pipeline.dataset import Dataset, SubDataset
from codeprep.prepconfig import PrepConfig, PrepParam


PATH_TO_DATASET_STUB = os.path.join('/', 'path', 'to', 'dataset')
PARSED_DATASETS_DIR = os.path.join('/', 'parsed', 'datasets')
PREP_DATASETS_DIR = os.path.join('/', 'prep', 'datasets')
OVERRIDDEN_PATH = os.path.join('/', 'overridden', 'path')


@mock.patch('os.path.exists', autospec=True, return_value=True)
@mock.patch('codeprep.pipeline.dataset.get_timestamp', autospec=True, return_value="01_01_01")
@mock.patch('codeprep.pipeline.dataset.DEFAULT_PARSED_DATASETS_DIR', PARSED_DATASETS_DIR)
@mock.patch('codeprep.pipeline.dataset.DEFAULT_PREP_DATASETS_DIR', PREP_DATASETS_DIR)
def test_non_bpe_split(get_timestamp_mock, os_exists_mock):
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })

    actual = Dataset.create(PATH_TO_DATASET_STUB, prep_config, None, None)

    assert actual._path == PATH_TO_DATASET_STUB
    assert actual._prep_config == prep_config
    assert actual._normalized_extension_list is None
    assert actual._custom_bpe_config is None
    assert actual._bpe_config is None
    assert actual._dataset_last_modified == '01_01_01'

    assert actual._original == SubDataset(actual, PATH_TO_DATASET_STUB, '')
    assert actual._parsed == SubDataset(actual, os.path.join(PARSED_DATASETS_DIR, 'dataset_01_01_01'), '.parsed')
    assert actual._preprocessed == SubDataset(actual, os.path.join(PREP_DATASETS_DIR, 'dataset_01_01_01_-_uc10su'), '.prep')


@mock.patch('os.path.exists', autospec=True, return_value=True)
@mock.patch('codeprep.pipeline.dataset.get_timestamp', autospec=True, return_value="01_01_01")
@mock.patch('codeprep.pipeline.dataset.DEFAULT_PARSED_DATASETS_DIR', PARSED_DATASETS_DIR)
@mock.patch('codeprep.pipeline.dataset.DEFAULT_PREP_DATASETS_DIR', PREP_DATASETS_DIR)
def test_non_bpe_split_with_one_extension(get_timestamp_mock, os_exists_mock):
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })

    actual = Dataset.create(PATH_TO_DATASET_STUB, prep_config, "java", None)

    assert actual._path == PATH_TO_DATASET_STUB
    assert actual._prep_config == prep_config
    assert actual._normalized_extension_list == ['java']
    assert actual._custom_bpe_config is None
    assert actual._bpe_config is None
    assert actual._dataset_last_modified == '01_01_01'

    assert actual._original == SubDataset(actual, PATH_TO_DATASET_STUB, '')
    assert actual._parsed == SubDataset(actual, os.path.join(PARSED_DATASETS_DIR, 'dataset_01_01_01_java'), '.parsed')
    assert actual._preprocessed == SubDataset(actual, os.path.join(PREP_DATASETS_DIR, 'dataset_01_01_01_java_-_uc10su'), '.prep')


@mock.patch('os.path.exists', autospec=True, return_value=True)
@mock.patch('codeprep.pipeline.dataset.get_timestamp', autospec=True, return_value="01_01_01")
@mock.patch('codeprep.pipeline.dataset.DEFAULT_PARSED_DATASETS_DIR', PARSED_DATASETS_DIR)
@mock.patch('codeprep.pipeline.dataset.DEFAULT_PREP_DATASETS_DIR', PREP_DATASETS_DIR)
def test_all_custom(get_timestamp_mock, os_exists_mock):
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })
    bpe_config = BpeConfig({
        BpeParam.CASE: 'yes',
        BpeParam.WORD_END: False,
        BpeParam.BASE: "code",
        BpeParam.UNICODE: "no",
    })

    custom_bpe_config = CustomBpeConfig("id", 1000, "/codes/file", "/cache/file")
    actual = Dataset.create(PATH_TO_DATASET_STUB, prep_config, "c|java", custom_bpe_config,
                            bpe_config, overriden_path_to_prep_dataset=OVERRIDDEN_PATH)

    assert actual._path == PATH_TO_DATASET_STUB
    assert actual._prep_config == prep_config
    assert actual._normalized_extension_list == ['c', 'java']
    assert actual._custom_bpe_config == custom_bpe_config
    assert actual._bpe_config == bpe_config
    assert actual._dataset_last_modified == '01_01_01'

    assert actual.original == SubDataset(actual, PATH_TO_DATASET_STUB, '')
    assert actual.parsed == SubDataset(actual, os.path.join(PARSED_DATASETS_DIR, 'dataset_01_01_01_c_java'), '.parsed')
    assert actual.preprocessed == SubDataset(actual, os.path.join(OVERRIDDEN_PATH, 'dataset_01_01_01_c_java_-_uc10su_id-1000_-_prep'), '.prep')
    assert actual.base_bpe_vocab_path == os.path.join(USER_CONFIG_DIR, VOCAB_DIR , 'dataset_01_01_01_c_java_-_U0EFsu')
    assert actual.bpe_path == os.path.join(USER_CONFIG_DIR, BPE_DIR , 'dataset_01_01_01_c_java_-_nounicode')
    assert actual.path_to_file_list_folder == os.path.join(USER_CACHE_DIR, 'file_lists' , 'dataset_01_01_01_c_java')
    assert actual.vocab_path == os.path.join(USER_CONFIG_DIR, VOCAB_DIR , 'dataset_01_01_01_c_java_-_uc10su_id-1000')