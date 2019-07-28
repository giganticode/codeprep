import logging
import os
import sys
import time
from typing import Optional, Dict, Callable, Tuple, List

import regex

from dataprep.bpepkg.bpe_config import BpeConfig
from dataprep.bpepkg.bpe_encode import read_merges
from dataprep.bpepkg.merge import MergeList
from dataprep.config import USER_BPE_DIR, USER_VOCAB_DIR

logger = logging.getLogger(__name__)

OTHER_VOCAB_FILE_NAME = "other_vocab"
BPE_REASSEMBLED_VOCAB_FILE_NAME = "bpe_vocab_reassembled.txt"
RESULTING_VOCAB_FILE_NAME = "vocab_res.txt"

MERGES_FILE_NAME = "merges.txt"
MERGES_CACHE_FILE_NAME = "merges_cache.txt"
BPE_CODES_ID_FILENAME = '.name'

USER_PREDEFINED_BPE_CODES = ['1k', '5k', '10k']
PREDEFINED_BPE_CODES = USER_PREDEFINED_BPE_CODES + ['0']


class InvalidBpeCodesIdError(Exception):
    pass


class CustomBpeConfig(object):
    def __init__(self, merge_list_id: str, n_merges: int, codes_file: str, cache_file: str):
        self.merge_list_id = merge_list_id
        self.n_merges = n_merges
        self.codes_file = codes_file
        self.cache_file = cache_file

    def can_use_cache_file(self):
        return self.cache_file and not self.n_merges

    @staticmethod
    def from_id(id_str: str) -> 'CustomBpeConfig':
        return CustomBpeConfig.create(*parse_merge_list_id(id_str))

    @staticmethod
    def create(merge_list_id: str, n_merges: int) -> 'CustomBpeConfig':
        dataset_bpe_dir = get_dataset_bpe_dir(merge_list_id)
        min_merges = get_min_merges(dataset_bpe_dir, limit=n_merges)
        # check if not None?
        dir_with_min_merges = os.path.join(dataset_bpe_dir, str(min_merges))
        if min_merges:
            if not n_merges == 0 or min_merges == n_merges:
                cache_file = os.path.join(dir_with_min_merges, MERGES_CACHE_FILE_NAME)
            else:
                cache_file = None
            return CustomBpeConfig(merge_list_id, n_merges, os.path.join(dir_with_min_merges, MERGES_FILE_NAME), cache_file)
        else:
            raise InvalidBpeCodesIdError(
                f"{n_merges} merges has not been computed for {merge_list_id}."
                f"Max possible value: {get_max_merges(dataset_bpe_dir)}")

    def __repr__(self):
        return f'{self.__class__.__name__} ({self.merge_list_id}, {self.n_merges}, {self.codes_file}, {self.cache_file})'


def is_predefined_id(id: str):
    return id in PREDEFINED_BPE_CODES


def get_codes_id_by_bpe_path(dataset_bpe_dir: str) -> Optional[str]:
    file_with_id = os.path.join(dataset_bpe_dir, BPE_CODES_ID_FILENAME)
    if not os.path.exists(file_with_id):
        return None
    else:
        with open(file_with_id, 'r') as f:
            return f.read().strip()


def create_new_id_from(path: str, bpe_config: BpeConfig, predefined_bpe_codes_id: Optional[str] = None) -> str:
    if predefined_bpe_codes_id:
        return predefined_bpe_codes_id
    else:
        name_parts = [os.path.basename(path)]
        id_suffix = bpe_config.to_suffix()
        if id_suffix:
            name_parts.append(id_suffix)
        id_base = '_'.join(name_parts)
        existing_ids = _get_all_custom_bpe_codes_and_max_merges().keys()
        if id_base not in existing_ids:
            return id_base
        else:
            def extract_number(full_id: str, id_base: str) -> int:
                m = regex.fullmatch(f"{id_base}_([0-9]+)", full_id)
                return int(m[1]) if m else 0

            numbers = list(map(lambda d: extract_number(d, id_base), existing_ids))
            new_number = max(numbers) + 1
            return f'{id_base}_{new_number}'


def write_bpe_codes_id(dataset_bpe_dir: str, bpe_codes_id: str) -> None:
    file_with_id = os.path.join(dataset_bpe_dir, BPE_CODES_ID_FILENAME)
    with open(file_with_id, 'w') as f:
        f.write(bpe_codes_id)


def parse_merge_list_id(s: str) -> Tuple[str, int]:
    REGEX = "(.*)-([1-9][0-9]*)$"
    m = regex.match(REGEX, s)
    if m:
        return m[1], int(m[2])
    else:
        raise InvalidBpeCodesIdError(f'Invalid id format: "{s}". Format should be: "{REGEX}"')


def get_base_vocab_dir(bpe_list_id: str) -> str:
    dataset_bpe_dir = get_dataset_bpe_dir(bpe_list_id)
    prep_config_str = os.path.basename(dataset_bpe_dir)
    #TODO do not hard code date and dir format in general
    m = regex.fullmatch(r'(.*?)((?:_-_.*)?)', prep_config_str)
    if not m:
        raise ValueError(f'Invalid dir format: {prep_config_str}')
    bpe_config = BpeConfig.from_suffix(m[2])
    base_prep_config = bpe_config.to_prep_config()
    return os.path.join(USER_VOCAB_DIR, f'{m[1]}_-_{base_prep_config}')


def get_dataset_bpe_dir(bpe_list_id: str) -> str:
    if not os.path.exists(USER_BPE_DIR):
        raise InvalidBpeCodesIdError(f"No custom bpe codes has been trained yet. "
                                     f"To train a custom bpe code run: `dataprep learn-bpe` command")

    bpe_dirs = next(os.walk(USER_BPE_DIR))[1]
    for dir in bpe_dirs:
        current_bpe_dir = os.path.join(USER_BPE_DIR, dir)
        current_id = get_codes_id_by_bpe_path(current_bpe_dir)
        if current_id and current_id == bpe_list_id:
            return current_bpe_dir
    raise InvalidBpeCodesIdError(f"Bpe id: {bpe_list_id} is not found. Possible values:\n {format_available_merge_list_ids()}")


def get_bpe_dir(merge_list_id: str, n_merges: int) -> str:
    bpe_dir = os.path.join(get_dataset_bpe_dir(merge_list_id), str(n_merges))
    if os.path.exists(bpe_dir):
        return bpe_dir
    else:
        raise InvalidBpeCodesIdError(f'Dir {bpe_dir} not found.')


def load_bpe_merges(merge_list_id: str, n_merges: int) -> MergeList:
    custom_bpe_config = CustomBpeConfig.create(merge_list_id, n_merges)
    return read_merges(custom_bpe_config.codes_file, n_merges)


def format_available_merge_list_ids() -> str:
    res = ""
    for k, v in _get_all_custom_bpe_codes_and_max_merges().items():
        res += f'{k}-[1..{v}]\n'
    return res


def _get_extreme_n_merges(root_bpe_dir: str, limit: int, init_val: int, in_order: Callable[[int, int, int], bool]):
    subdirs = _get_all_bpe_merges_dirs(root_bpe_dir)
    extreme_value = init_val
    for subdir in subdirs:
        try:
            num = int(subdir)
            if in_order(extreme_value, num, limit):
                extreme_value = num
        except ValueError:
            pass # for the case of part_vocab folder for example
    if extreme_value != init_val:
        return extreme_value
    else:
        return None


def get_min_merges(dataset_bpe_dir: str, limit: Optional[int]=0) -> Optional[int]:
    return _get_extreme_n_merges(dataset_bpe_dir, limit, sys.maxsize, lambda e,n,l: e > n >= l)


def get_max_merges(dataset_bpe_dir: str, limit: Optional[int]=sys.maxsize) -> Optional[int]:
    return _get_extreme_n_merges(dataset_bpe_dir, limit, 0, lambda e,n,l: e < n <= l)


def _get_all_custom_bpe_codes_and_max_merges() -> Dict[str, int]:
    result = {}
    bpe_dirs = next(os.walk(USER_BPE_DIR))[1]
    for bpe_dir in bpe_dirs:
        path = os.path.join(USER_BPE_DIR, bpe_dir)
        code = get_codes_id_by_bpe_path(path)
        max_merges = get_max_merges(path)
        if code and max_merges:
            result[code] = max_merges
    return result


def _get_all_bpe_merges_dirs(dataset_bpe_dir: str) -> List[str]:
    if not os.path.exists(dataset_bpe_dir):
        raise FileNotFoundError(f'Directory {dataset_bpe_dir} does not exist!')
    return next(os.walk(dataset_bpe_dir))[1]


def archive_existing_common_bpe_folder(dataset_bpe_dir: str) -> None:
    if os.path.exists(dataset_bpe_dir):
        logger.info(f'Archiving existing bpe dir. '
                    f'{dataset_bpe_dir} -> {dataset_bpe_dir}.{str(int(time.time()))}')
        os.rename(dataset_bpe_dir, f'{dataset_bpe_dir}.{str(int(time.time()))}')