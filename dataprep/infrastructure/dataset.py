import ast
import logging
import os
from typing import Type, Optional, Generator, List

from dataprep.bpepkg.bpe_config import BpeConfig
from dataprep.config import DEFAULT_PARSED_DATASETS_DIR, DEFAULT_PREP_DATASETS_DIR, USER_BPE_DIR, DEFAULT_FILE_LIST_DIR, \
    USER_VOCAB_DIR, DEFAULT_CORPUS_SIZES_DIR
from dataprep.dirutils import walk_and_save, get_timestamp
from dataprep.infrastructure.bperegistry import get_codes_id_by_bpe_path, create_new_id_from, write_bpe_codes_id, \
    CustomBpeConfig
from dataprep.prepconfig import PrepConfig
from dataprep.vocab import VOCAB_FILENAME

logger = logging.getLogger(__name__)

PP_PARAMS_FILENAME = 'params.json'
PREPROCESSING_TYPES_FILENAME = 'preprocessing_types.json'
FILE_LIST_FILENAME = "filelist"
DIR_LIST_FILENAME = "dirlist"

PARSED_EXTENSION = ".parsed"
PREPROCESSED_EXTENSION = ".prep"
NOT_FINISHED_EXTENSION = ".part"
ARCHIVED_EXT = "archived"

NONBPE_VOCAB_FILENAME = 'nonbpe_vocab'


class SubDataset(object):
    def __init__(self, dataset: 'Dataset', path: str, suffix: str = ''):
        self._dataset = dataset
        self._path = path
        self._suffix = suffix

    @property
    def dataset(self):
        return self._dataset

    @property
    def path(self) -> str:
        return self._path

    def set_ready(self) -> None:
        set_path_ready(self.path)

    def is_outdated(self) -> bool:
        return is_path_outdated(self.path)

    def file_iterator(self) -> Generator[bytes, None, None]:
        encoded_path = self.path.encode()
        encoded_suffix = self._suffix.encode()
        for file in self._dataset.get_all_files():
            if os.path.isfile(encoded_path):
                yield encoded_path + encoded_suffix
            else:
                yield os.path.join(encoded_path, file + encoded_suffix)

    def get_new_file_name(self, file_path: bytes, new_subdataset: 'SubDataset') -> bytes:
        encoded_path = self.path.encode()
        rel_path = os.path.relpath(file_path, encoded_path)
        if rel_path == '.'.encode(): # this check is needed and the result is true for cases when only one file is being preprocessed
            rel_path = os.path.basename(file_path)
        return os.path.join(new_subdataset.path.encode(),
                            (rel_path[:-len(self._suffix.encode())] if len(self._suffix.encode()) else rel_path) + new_subdataset._suffix.encode())

    def ready(self) -> bool:
        return is_path_ready(self.path)

    def archive(self) -> None:
        archive_path(self.path)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, SubDataset):
            return self._dataset.path == o._dataset.path and self._path == o._path and self._suffix == o._suffix
        return False

    def __repr__(self) -> str:
        return f'{self.__class__.__name__} ({self._dataset}, {self._path}, {self._suffix}) '

    def __str__(self) -> str:
        return self._path


class Dataset(object):
    """
    Abstaction that incapsulates the location of the dataset in the file system and assures integrity of intermediate
    representation of data when the data preprocessing operation consists of multiple steps.
    """
    def __init__(self, path: str, prep_config: PrepConfig, normalized_extension_list: Optional[List[str]],
                 custom_bpe_config: Optional[CustomBpeConfig],
                 bpe_config: Optional[BpeConfig],
                 overridden_path_to_prep_dataset):
        self._path = path
        self._prep_config = prep_config
        self._normalized_extension_list = normalized_extension_list
        self._custom_bpe_config = custom_bpe_config
        self._bpe_config = bpe_config
        self._dataset_last_modified = get_timestamp(path)

        self._original = SubDataset(self, self.path)
        self._parsed = SubDataset(self, self._get_path_to_parsed_dataset(), suffix=PARSED_EXTENSION)
        self._preprocessed = SubDataset(self, self._get_path_to_prep_dataset(overridden_path_to_prep_dataset), suffix=PREPROCESSED_EXTENSION)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Dataset):
            return self._path == o._path and \
                   self._prep_config == o._prep_config and \
                   self._normalized_extension_list == o._normalized_extension_list and \
                   self._custom_bpe_config == o._custom_bpe_config and \
                   self._bpe_config == o._bpe_config and \
                   self._dataset_last_modified == o._dataset_last_modified and \
                   self._original == o._original and \
                   self._parsed == o._parsed and \
                   self._preprocessed == o._preprocessed
        return False

    #####################################################

    @classmethod
    def create(cls: Type['Dataset'], path_to_dataset: str, prep_config: PrepConfig, extensions: Optional[str],
               custom_bpe_config: Optional[CustomBpeConfig],
               bpe_config: Optional[BpeConfig] = None,
               overriden_path_to_prep_dataset: Optional[str] = None) -> 'Dataset':
        if not os.path.exists(path_to_dataset):
            raise ValueError(f"Path {path_to_dataset} does not exist")

        normalized_extension_list = normalize_extension_string(extensions)
        dataset = cls(path_to_dataset, prep_config, normalized_extension_list, custom_bpe_config, bpe_config, overriden_path_to_prep_dataset)

        if not os.path.exists(dataset.parsed.path):
            os.makedirs(dataset.parsed.path)

        if not os.path.exists(dataset.preprocessed.path):
            os.makedirs(dataset.preprocessed.path)

        if not os.path.exists(DEFAULT_FILE_LIST_DIR):
            os.makedirs(DEFAULT_FILE_LIST_DIR)

        if not os.path.exists(DEFAULT_CORPUS_SIZES_DIR):
            os.makedirs(DEFAULT_CORPUS_SIZES_DIR)

        if not os.path.exists(dataset.bpe_path):
            os.makedirs(dataset.bpe_path)

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
        name = f'{self.name}_{self.dataset_last_modified}'
        if self._normalized_extension_list:
            name += ('_' + "_".join(self._normalized_extension_list))
        return name

    @property
    def parsed(self) -> SubDataset:
        return self._parsed

    @property
    def preprocessed(self) -> SubDataset:
        return self._preprocessed

    def _get_path_to_parsed_dataset(self) -> str:
        return os.path.join(DEFAULT_PARSED_DATASETS_DIR, self.get_dataset_dir_name)

    def _get_prep_suffix(self) -> str:
        suffix = str(self.prep_config)
        if self._custom_bpe_config:
            suffix += f'_{self._custom_bpe_config.merge_list_id}-{self._custom_bpe_config.n_merges}'
        return suffix

    def _get_path_to_prep_dataset(self, overriden_path_to_prep_dataset: Optional[str]) -> str:
        prefix = overriden_path_to_prep_dataset if overriden_path_to_prep_dataset else DEFAULT_PREP_DATASETS_DIR

        basename = f'{self.get_dataset_dir_name}_-_{self._get_prep_suffix()}'

        if overriden_path_to_prep_dataset:
            basename += '_-_prep'

        return os.path.join(prefix, basename)

    @property
    def original(self) -> SubDataset:
        return self._original

    @property
    def bpe_path(self) -> str:
        name_parts = [self.get_dataset_dir_name]
        if self._bpe_config:
            suffix = self._bpe_config.to_suffix()
            if suffix:
                name_parts.append(suffix)

        return os.path.join(USER_BPE_DIR, "_-_".join(name_parts))

    @property
    def base_bpe_vocab_path(self) -> str:
        return os.path.join(USER_VOCAB_DIR, f'{self.get_dataset_dir_name}_-_{self._bpe_config.to_prep_config()}')

    @property
    def vocab_path(self) -> str:
        return os.path.join(USER_VOCAB_DIR, f'{self.get_dataset_dir_name}_-_{self._get_prep_suffix()}')

    @property
    def path_to_vocab_file(self) -> str:
        return os.path.join(self.vocab_path, VOCAB_FILENAME)

    @property
    def path_to_bpe_vocab_file(self) -> str:
        return os.path.join(self.base_bpe_vocab_path, VOCAB_FILENAME)

    @property
    def path_to_nonbpe_vocab_file(self) -> str:
        return os.path.join(self.base_bpe_vocab_path if self._bpe_config else self.vocab_path, NONBPE_VOCAB_FILENAME)

    @property
    def bpe_codes_id(self) -> Optional[str]:
        return get_codes_id_by_bpe_path(self.bpe_path)

    def assign_bpe_codes_id(self, bpe_config: BpeConfig, predefined_bpe_codes_id: str) -> None:
        id = create_new_id_from(self.path, bpe_config, predefined_bpe_codes_id)
        write_bpe_codes_id(self.bpe_path, id)

    @property
    def path_to_file_list_folder(self) -> str:
        return os.path.join(DEFAULT_FILE_LIST_DIR, f'{self.get_dataset_dir_name}')

    @property
    def path_to_prep_corpus_size_file(self) -> str:
        return os.path.join(DEFAULT_CORPUS_SIZES_DIR, f'{os.path.basename(self.preprocessed.path)}')

    def get_all_files(self, return_dirs_instead_of_regular_files: bool=False) -> Generator[bytes, None, None]:
        if self.files_need_to_be_saved():
            if not os.path.exists(self.path_to_file_list_folder):
                os.makedirs(self.path_to_file_list_folder)
            for filepath in walk_and_save(self.original.path,
                                          os.path.join(self.path_to_file_list_folder, DIR_LIST_FILENAME),
                                          os.path.join(self.path_to_file_list_folder, FILE_LIST_FILENAME),
                                          return_dirs_instead_of_regular_files, self._normalized_extension_list):
                yield filepath
            set_path_ready(self.path_to_file_list_folder)
        else:
            file_to_save_to = DIR_LIST_FILENAME if return_dirs_instead_of_regular_files else FILE_LIST_FILENAME
            with open(os.path.join(self.path_to_file_list_folder, file_to_save_to)) as f:
                for line in f:
                    yield ast.literal_eval(line)

    ###################################

    def to_summary(self) -> str:
        return f"Original dataset: {self.original.path}\nParsed dataset (internal): {self.parsed.path}\nPreprocessed dataset: {self.preprocessed.path}"

    def __str__(self) -> str:
        return self.to_summary()

    def files_need_to_be_saved(self) -> bool:
        return not is_path_ready(self.path_to_file_list_folder) or is_path_outdated(self.path_to_file_list_folder)


def _get_last_modif_file_path_for_dir(path: str) -> str:
    dirname, filename = os.path.split(path)
    return os.path.join(dirname, f'.{filename}.lastmodif')


def set_path_ready(path: str) -> None:
    modif_file = _get_last_modif_file_path_for_dir(path)
    with open(modif_file, 'w') as f:
        f.write(get_timestamp(path))


def is_path_outdated(path: str) -> bool:
    modif_file = _get_last_modif_file_path_for_dir(path)
    if not os.path.exists(modif_file):
        raise FileNotFoundError()
    with open(modif_file) as f:
        expected_timestamp = f.read()
        actual_timestamp = get_timestamp(path)
        return (expected_timestamp != actual_timestamp)


def is_path_ready(path: str) -> bool:
    if not os.path.exists(path):
        return False
    modif_file = _get_last_modif_file_path_for_dir(path)
    return os.path.exists(modif_file)


def archive_path(path: str) -> None:
    modif_file = _get_last_modif_file_path_for_dir(path)
    timestamp = get_timestamp(path)
    if not os.path.exists(DEFAULT_PREP_DATASETS_DIR):
        os.makedirs(DEFAULT_PREP_DATASETS_DIR)
    os.rename(path, os.path.join(DEFAULT_PREP_DATASETS_DIR, f'{os.path.basename(path)}.{ARCHIVED_EXT}.{timestamp}'))
    os.rename(modif_file, os.path.join(DEFAULT_PREP_DATASETS_DIR, f'{os.path.basename(modif_file)}.{ARCHIVED_EXT}.{timestamp}'))


def normalize_extension_string(extensions: Optional[str]) -> Optional[List[str]]:
    if not extensions:
        return extensions

    exts = extensions.split("|")
    unique_ext = set(exts)
    return sorted(unique_ext)