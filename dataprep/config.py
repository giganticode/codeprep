import os

import appdirs

TRAIN_DIR = 'train'
TEST_DIR = 'test'
VALID_DIR = 'valid'

CASE_DIR='case'
NO_CASE_DIR='nocase'

REPR_DIR = 'repr'
PARSED_DIR = 'parsed'
BPE_DIR = 'bpe'
VOCAB_DIR = 'vocab'

current_script_location = os.path.realpath(__file__)
root_package_dir = os.path.dirname(current_script_location)
data_dir = os.path.join(root_package_dir, 'data')

app_name='dataprep'

with open(os.path.join(root_package_dir, 'VERSION')) as version_file:
    version = version_file.read().strip()

USER_CONFIG_DIR = appdirs.user_config_dir(app_name, appauthor=False, version=version)
USER_CACHE_DIR = appdirs.user_cache_dir(app_name, appauthor=False, version=version)

DEFAULT_FILE_LIST_DIR = os.path.join(USER_CACHE_DIR, 'file_lists')
DEFAULT_PARSED_DATASETS_DIR = os.path.join(USER_CACHE_DIR, 'parsed_datasets')
DEFAULT_PREP_DATASETS_DIR = os.path.join(USER_CACHE_DIR, 'prep_datasets')
DEFAULT_BPE_DIR = os.path.join(data_dir, BPE_DIR)
USER_BPE_DIR = os.path.join(USER_CONFIG_DIR, BPE_DIR)
USER_VOCAB_DIR = os.path.join(USER_CONFIG_DIR, VOCAB_DIR)
DEFAULT_BPE_CACHE_DIR = os.path.join(USER_CACHE_DIR, BPE_DIR)
DEFAULT_CORPUS_SIZES_DIR = os.path.join(USER_CACHE_DIR, 'corpus_sizes')

REWRITE_PARSED_FILE=False
REWRITE_PREPROCESSED_FILE=False

CHUNKSIZE=24
LIMIT_FILES_ON_LAST_MODIFICATION_CHECK=15000
LIMIT_FILES_SCANNING=50000
