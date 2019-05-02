import logging
import os
from datetime import datetime

from typing import Type, Optional

from dataprep.config import DEFAULT_PARSED_DATASETS_DIR, DEFAULT_PREP_DATASETS_DIR, USER_BPE_DIR
from dataprep.prepconfig import PrepConfig
from dataprep.split.bpe_config import BpeConfig
logger = logging.getLogger(__name__)

PP_PARAMS_FILENAME = 'params.json'
PREPROCESSING_TYPES_FILENAME = 'preprocessing_types.json'
BPE_VOCAB_FILE_NAME = "bpe_vocab"

PARSED_EXTENSION = "parsed"
PREPROCESSED_EXTENSION = "prep"
NOT_FINISHED_EXTENSION = "part"
ARCHIVED_EXT = "archived"


class SubDataset(object):
    def __init__(self, path, extension: Optional[str] = None):
        self._path = path
        self._extension = extension

    @property
    def path(self):
        return self._path

    def set_ready(self):
        modif_file = _get_last_modif_file_path_for_dir(self.path)
        with open(modif_file, 'w') as f:
            f.write(get_timestamp_for_folder(self.path))

    def is_up_to_date(self):
        modif_file = _get_last_modif_file_path_for_dir(self.path)
        if not os.path.exists(modif_file):
            raise FileNotFoundError()
        with open(modif_file) as f:
            return f.read() == get_timestamp_for_folder(self.path)

    def file_iterator(self):
        if os.path.isfile(self.path):
            yield self.path
        else:
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    if not self._extension or file.endswith(f".{self._extension}"):
                        yield os.path.join(root, file)

    def get_new_file_name(self, file_path: str, new_subdataset: 'SubDataset') -> str:
        rel_path = os.path.relpath(file_path, self.path)
        if rel_path == '.': # this check is needed and the result is true for cases when only one file is being preprocessed
            rel_path = os.path.basename(file_path)
        return os.path.join(new_subdataset.path, rel_path[:-len(self._extension)] + new_subdataset._extension)

    def ready(self):
        if not os.path.exists(self.path):
            return False
        modif_file = _get_last_modif_file_path_for_dir(self.path)
        return os.path.exists(modif_file)

    def archive(self):
        modif_file = _get_last_modif_file_path_for_dir(self.path)
        timestamp = get_timestamp_for_folder(self.path)
        if not os.path.exists(DEFAULT_PREP_DATASETS_DIR):
            os.makedirs(DEFAULT_PREP_DATASETS_DIR)
        os.rename(self.path, os.path.join(DEFAULT_PREP_DATASETS_DIR, f'{os.path.basename(self.path)}.{ARCHIVED_EXT}.{timestamp}'))
        os.rename(modif_file, os.path.join(DEFAULT_PREP_DATASETS_DIR, f'{os.path.basename(modif_file)}.{ARCHIVED_EXT}.{timestamp}'))


class Dataset(object):
    """
    Abstaction that incapsulates the location of the dataset in the file system and assures integrity of intermediate
    representation of data when the data preprocessing operation consists of multiple steps.
    """
    def __init__(self, path: str, prep_config: PrepConfig, extension: Optional[str],
                 bpe_config: Optional[BpeConfig],
                 overridden_path_to_prep_dataset):
        self._path = path
        self._prep_config = prep_config
        self._bpe_config = bpe_config
        self._dataset_last_modified = get_timestamp_for_folder(path)

        self._original = SubDataset(self.path, extension)
        self._parsed = SubDataset(self._get_path_to_parsed_dataset(), PARSED_EXTENSION)
        self._preprocessed = SubDataset(self._get_path_to_prep_dataset(overridden_path_to_prep_dataset), PREPROCESSED_EXTENSION)
        self._bpe = SubDataset(os.path.join(USER_BPE_DIR, self.name))

    #####################################################

    @classmethod
    def create(cls: Type['Dataset'], path_to_dataset: str, prep_config: PrepConfig, extension: str,
               bpe_config: Optional[BpeConfig] = None,
               overriden_path_to_prep_dataset: Optional[str] = None) -> 'Dataset':
        if not os.path.exists(path_to_dataset):
            raise ValueError(f"Path {path_to_dataset} does not exist")

        dataset = cls(path_to_dataset, prep_config, extension, bpe_config, overriden_path_to_prep_dataset)

        if not os.path.exists(dataset.parsed.path):
            os.makedirs(dataset.parsed.path)

        if not os.path.exists(dataset.preprocessed.path):
            os.makedirs(dataset.preprocessed.path)

        return dataset

    #####################################################

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        return os.path.basename(self.path)

    @property
    def dataset_last_modified(self) -> str:
        return self._dataset_last_modified

    @property
    def prep_config(self) -> PrepConfig:
        return self._prep_config

    @property
    def get_dataset_dir_name(self) -> str:
        return f'{self.name}_{get_timestamp_for_folder(self.path)}'

    @property
    def parsed(self) -> SubDataset:
        return self._parsed

    @property
    def preprocessed(self) -> SubDataset:
        return self._preprocessed

    def _get_path_to_parsed_dataset(self) -> str:
        return os.path.join(DEFAULT_PARSED_DATASETS_DIR, self.get_dataset_dir_name)

    def _get_path_to_prep_dataset(self, overriden_path_to_prep_dataset: Optional[str]) -> str:
        if overriden_path_to_prep_dataset:
            return overriden_path_to_prep_dataset

        if overriden_path_to_prep_dataset == '':
            return f'{self.path}_{self.dataset_last_modified}_preprocessed_{self.prep_config}'

        return os.path.join(DEFAULT_PREP_DATASETS_DIR, self.get_dataset_dir_name)

    @property
    def bpe(self) -> SubDataset:
        return self._bpe

    @property
    def original(self) -> SubDataset:
        return self._original

    @property
    def path_to_bpe_vocab_file(self) -> str:
        return os.path.join(self.bpe.path, BPE_VOCAB_FILE_NAME)

    ###################################

    def to_summary(self) -> str:
        return f"Original dataset: {self.original.path}\nParsed dataset (internal): {self.parsed.path}\nPreprocessed dataset: {self.preprocessed.path}"


def _get_last_modif_file_path_for_dir(path: str) -> str:
    dirname, filename = os.path.split(path)
    return os.path.join(dirname, f'.{filename}.lastmodif')


def get_dir_last_modification(path: str) -> datetime:
    def get_m_time_recursively(path):
        yield os.path.getmtime(path)
        for root, _, _ in os.walk(path):
            yield os.path.getmtime(root)

    mtime = max(get_m_time_recursively(path))
    return datetime.fromtimestamp(mtime)


def get_timestamp_for_folder(path: str) -> str:
    last_modif_time = get_dir_last_modification(path)
    return last_modif_time.strftime("%y-%m-%dT%H-%M-%S")
