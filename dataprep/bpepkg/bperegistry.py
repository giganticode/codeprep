import logging
import os
import sys

import re
import time
from typing import Optional, Tuple, Dict

from dataprep.bpepkg.bpe_config import BpeConfig
from dataprep.bpepkg.bpe_encode import read_merges
from dataprep.bpepkg.merge import MergeList
from dataprep.config import USER_BPE_DIR

logger = logging.getLogger(__name__)


MERGES_FILE_NAME = "merges.txt"
MERGES_CACHE_FILE_NAME = "merges_cache.txt"
BPE_CODES_ID_FILENAME = '.name'

PREDEFINED_BPE_CODES = ['1k', '5k', '10k']


class InvalidBpeCodesIdError(Exception):
    pass


class CustomBpeConfig(object):
    def __init__(self, id: str, n_merges: int, codes_file: str, cache_file: str):
        self.id = id
        self.n_merges = n_merges
        self.codes_file = codes_file
        self.cache_file = cache_file

    def can_use_cache_file(self):
        return self.cache_file and not self.n_merges

    def __repr__(self):
        return f'{self.__class__.__name__} ({self.id}, {self.n_merges}, {self.codes_file}, {self.cache_file})'


def is_predefined_id(id):
    return id in PREDEFINED_BPE_CODES


def get_codes_id_by_bpe_path(path: str) -> Optional[str]:
    file_with_id = os.path.join(path, BPE_CODES_ID_FILENAME)
    if not os.path.exists(file_with_id):
        return None
    else:
        with open(file_with_id, 'r') as f:
            return f.read().strip()


def create_new_id_from(path: str, bpe_config: BpeConfig, predefined_bpe_codes_id: Optional[str] = None) -> str:
    if predefined_bpe_codes_id:
        return predefined_bpe_codes_id
    else:
        id_base = f'{os.path.basename(path)}{bpe_config.to_suffix()}'
        existing_ids = get_all_custom_bpe_codes_with_max_merges().keys()
        if id_base not in existing_ids:
            return id_base
        else:
            def extract_number(full_id: str, id_base: str) -> int:
                m = re.match(f"{id_base}_([0-9]*)", full_id)
                return int(m[1]) if m else 0

            numbers = list(map(lambda d: extract_number(d, id_base), existing_ids))
            new_number = max(numbers) + 1
            return f'{id_base}_{new_number}'


def write_bpe_codes_id(bpe_path: str, bpe_codes_id: str) -> None:
    file_with_id = os.path.join(bpe_path, BPE_CODES_ID_FILENAME)
    with open(file_with_id, 'w') as f:
        f.write(bpe_codes_id)


def parse_bpe_codes_id(s: str) -> Tuple[str, int]:
    REGEX = "(.*)-([1-9][0-9]*)$"
    m = re.match(REGEX, s)
    if m:
        return m[1], int(m[2])
    else:
        raise InvalidBpeCodesIdError(f'Invalid id format: "{s}". Format should be: "{REGEX}"')


def get_bpe_dir_by_id(id: str) -> str:
    if not os.path.exists(USER_BPE_DIR):
        raise InvalidBpeCodesIdError(f"No custom bpe codes has been trained yet. "
                                     f"To train a custom bpe code run: `dataprep learn-bpe` command")

    bpe_codes_id, _ = parse_bpe_codes_id(id)
    bpe_dirs = next(os.walk(USER_BPE_DIR))[1]
    for dir in bpe_dirs:
        current_bpe_dir = os.path.join(USER_BPE_DIR, dir)
        current_id = get_codes_id_by_bpe_path(current_bpe_dir)
        if current_id and current_id == bpe_codes_id:
            return current_bpe_dir
    raise InvalidBpeCodesIdError(f"Bpe id: {id} is not found. Possible values:\n {format_available_bpe_ids()}")


def create_custom_bpe_config(id: str) -> CustomBpeConfig:
    bpe_dir = get_bpe_dir_by_id(id)
    bpe_codes_id, n_merges = parse_bpe_codes_id(id)
    min_merges = get_min_merges(bpe_dir, limit=n_merges)
    dir_with_min_merges = os.path.join(bpe_dir, str(min_merges))
    if min_merges:
        if not n_merges or min_merges == n_merges:
            cache_file = os.path.join(dir_with_min_merges, MERGES_CACHE_FILE_NAME)
        else:
            cache_file = None
        return CustomBpeConfig(id, n_merges, os.path.join(dir_with_min_merges, MERGES_FILE_NAME), cache_file)
    else:
        raise InvalidBpeCodesIdError(f"{n_merges} merges has not been computed for {bpe_codes_id}."
                                     f"Max possible value: {get_max_merges(bpe_dir)}")


def load_bpe_merges(bpe_id: str) -> MergeList:
    custom_bpe_config = create_custom_bpe_config(bpe_id)
    return read_merges(custom_bpe_config.codes_file, custom_bpe_config.n_merges)


def format_available_bpe_ids() -> str:
    res = ""
    for k, v in get_all_custom_bpe_codes_with_max_merges().items():
        res += f'{k}-[1..{v}]\n'
    return res


def get_min_merges(dataset_bpe_dir: str, limit: Optional[int]=0) -> Optional[int]:
    subdirs = get_all_bpe_merges_dirs(dataset_bpe_dir)
    min_number = sys.maxsize
    for subdir in subdirs:
        try:
            num = int(subdir)
            if min_number > num >= limit:
                min_number = num
        except ValueError:
            pass # for the case of part_vocab folder for example
    if min_number != sys.maxsize:
        return min_number
    else:
        return None


def get_max_merges(dataset_bpe_dir: str, limit: Optional[int]=sys.maxsize) -> Optional[int]:
    subdirs = get_all_bpe_merges_dirs(dataset_bpe_dir)
    max_number = 0
    for subdir in subdirs:
        try:
            num = int(subdir)
            if max_number < num <= limit:
                max_number = num
        except ValueError:
            pass # for the case of part_vocab folder for example
    if max_number != 0:
        return max_number
    else:
        return None


def get_all_custom_bpe_codes_with_max_merges() -> Dict[str, int]:
    result = {}
    bpe_dirs = next(os.walk(USER_BPE_DIR))[1]
    for bpe_dir in bpe_dirs:
        path = os.path.join(USER_BPE_DIR, bpe_dir)
        code = get_codes_id_by_bpe_path(path)
        max_merges = get_max_merges(path)
        if code and max_merges:
            result[code] = max_merges
    return result


def get_all_bpe_merges_dirs(dataset_bpe_dir: str):
    if not os.path.exists(dataset_bpe_dir):
        raise FileNotFoundError(f'Directory {dataset_bpe_dir} does not exist!')
    return next(os.walk(dataset_bpe_dir))[1]


def archive_existing_common_bpe_folder(dataset_bpe_dir: str) -> None:
    if os.path.exists(dataset_bpe_dir):
        logger.info(f'Archiving existing bpe dir. '
                    f'{dataset_bpe_dir} -> {dataset_bpe_dir}.{str(int(time.time()))}')
        os.rename(dataset_bpe_dir, f'{dataset_bpe_dir}.{str(int(time.time()))}')