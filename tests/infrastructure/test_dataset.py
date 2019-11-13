import os
from unittest import mock

from dataprep.bpepkg.bpe_config import BpeConfig, BpeParam
from dataprep.config import USER_CONFIG_DIR, VOCAB_DIR, BPE_DIR, USER_CACHE_DIR
from dataprep.infrastructure.bperegistry import CustomBpeConfig
from dataprep.infrastructure.dataset import Dataset, SubDataset
from dataprep.prepconfig import PrepConfig, PrepParam


@mock.patch('os.path.exists', autospec=True, return_value=True)
@mock.patch('dataprep.infrastructure.dataset.get_timestamp', autospec=True, return_value="01_01_01")
@mock.patch('dataprep.infrastructure.dataset.DEFAULT_PARSED_DATASETS_DIR', '/parsed/dataset')
@mock.patch('dataprep.infrastructure.dataset.DEFAULT_PREP_DATASETS_DIR', '/prep/dataset')
def test_non_bpe_split(get_timestamp_mock, os_exists_mock):
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })

    actual = Dataset.create('/path/to/dataset', prep_config, None, None)

    assert '/path/to/dataset' == actual._path
    assert prep_config == actual._prep_config
    assert actual._normalized_extension_list is None
    assert actual._custom_bpe_config is None
    assert actual._bpe_config is None
    assert '01_01_01', actual._dataset_last_modified

    assert SubDataset(actual, '/path/to/dataset', '') == actual._original
    assert SubDataset(actual, '/parsed/dataset/dataset_01_01_01', '.parsed') == actual._parsed
    assert SubDataset(actual, '/prep/dataset/dataset_01_01_01_-_uc10su', '.prep') == actual._preprocessed


@mock.patch('os.path.exists', autospec=True, return_value=True)
@mock.patch('dataprep.infrastructure.dataset.get_timestamp', autospec=True, return_value="01_01_01")
@mock.patch('dataprep.infrastructure.dataset.DEFAULT_PARSED_DATASETS_DIR', '/parsed/dataset')
@mock.patch('dataprep.infrastructure.dataset.DEFAULT_PREP_DATASETS_DIR', '/prep/dataset')
def test_non_bpe_split_with_one_extension(get_timestamp_mock, os_exists_mock):
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })

    actual = Dataset.create('/path/to/dataset', prep_config, "java", None)

    assert '/path/to/dataset' == actual._path
    assert prep_config == actual._prep_config
    assert ['java'] == actual._normalized_extension_list
    assert actual._custom_bpe_config is None
    assert actual._bpe_config is None
    assert '01_01_01' == actual._dataset_last_modified

    assert SubDataset(actual, '/path/to/dataset', ''), actual._original
    assert SubDataset(actual, '/parsed/dataset/dataset_01_01_01_java', '.parsed'), actual._parsed
    assert SubDataset(actual, '/prep/dataset/dataset_01_01_01_java_-_uc10su', '.prep'), actual._preprocessed


@mock.patch('os.path.exists', autospec=True, return_value=True)
@mock.patch('dataprep.infrastructure.dataset.get_timestamp', autospec=True, return_value="01_01_01")
@mock.patch('dataprep.infrastructure.dataset.DEFAULT_PARSED_DATASETS_DIR', '/parsed/dataset')
@mock.patch('dataprep.infrastructure.dataset.DEFAULT_PREP_DATASETS_DIR', '/prep/dataset')
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
    actual = Dataset.create('/path/to/dataset', prep_config, "c|java", custom_bpe_config,
                            bpe_config, overriden_path_to_prep_dataset="/path/overridden")

    assert '/path/to/dataset' == actual._path
    assert prep_config == actual._prep_config
    assert ['c', 'java'] == actual._normalized_extension_list
    assert custom_bpe_config == actual._custom_bpe_config
    assert bpe_config == actual._bpe_config
    assert '01_01_01' == actual._dataset_last_modified

    assert SubDataset(actual, '/path/to/dataset', '') == actual.original
    assert SubDataset(actual, '/parsed/dataset/dataset_01_01_01_c_java', '.parsed') == actual.parsed
    assert SubDataset(actual, '/path/overridden/dataset_01_01_01_c_java_-_uc10su_id-1000_-_prep', '.prep') == actual.preprocessed
    assert os.path.join(USER_CONFIG_DIR, VOCAB_DIR , 'dataset_01_01_01_c_java_-_U0EFsu') == actual.base_bpe_vocab_path
    assert os.path.join(USER_CONFIG_DIR, BPE_DIR , 'dataset_01_01_01_c_java_-_nounicode') == actual.bpe_path
    assert os.path.join(USER_CACHE_DIR, 'file_lists' , 'dataset_01_01_01_c_java') == actual.path_to_file_list_folder
    assert os.path.join(USER_CONFIG_DIR, VOCAB_DIR , 'dataset_01_01_01_c_java_-_uc10su_id-1000') == actual.vocab_path