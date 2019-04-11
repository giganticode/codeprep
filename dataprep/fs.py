import json
import logging
import os
from typing import Optional, TypeVar, Type

from dataprep.config import PARSED_DIR, DEFAULT_PARSED_DATASETS_DIR
from dataprep.util import get_two_levels_subdirs

logger = logging.getLogger(__name__)

PP_PARAMS_FILENAME = 'params.json'
PREPROCESSING_TYPES_FILENAME = 'preprocessing_types.json'

T = TypeVar('T', bound='FS')


class FS(object):
    def __init__(self, path_to_dataset: str, repr: Optional[str]):
        self._path_to_dataset = path_to_dataset
        self._repr = repr

    #####################################################

    @classmethod
    def for_parse_projects(cls: Type[T], path_to_dataset: str) -> T:
        if not os.path.exists(path_to_dataset):
            raise ValueError(f"Path {path_to_dataset} does not exist")

        fs = cls(path_to_dataset, None)

        if not os.path.exists(fs.path_to_parsed_dataset):
            os.makedirs(fs.path_to_parsed_dataset)

        return fs

    #####################################################


    @property
    def path_to_dataset(self):
        return self._path_to_dataset

    @property
    def dataset(self) -> str:
        return os.path.basename(self.path_to_dataset)

    @property
    def repr(self) -> str:
        return self._repr

    #################################################

    @property
    def path_to_parsed_dataset(self) -> str:
        return os.path.join(DEFAULT_PARSED_DATASETS_DIR, self.dataset)


    ###################################

    def get_raw_projects(self):
        for _, train_test_valid, project in get_two_levels_subdirs(self.path_to_dataset):
            yield (train_test_valid, project)
