import argparse
import gzip
import logging
import os
import pickle
from abc import ABCMeta, abstractmethod
from multiprocessing.pool import Pool
from typing import Optional, List

import jsons
from tqdm import tqdm

from dataprep.preprocessors.general import to_token_list
from dataprep.prepconfig import PrepParam, get_types_to_be_repr, PrepConfig
from dataprep.preprocessors.repr import to_repr_list, ReprConfig
from dataprep.split.bpe_encode import read_merges
from dataprep.split.ngram import NgramSplittingType, NgramSplitConfig
from dataprep.util import read_dict_from_2_columns
from dataprep.config import DEFAULT_PARSED_DATASETS_DIR, DEFAULT_BPE_DIR, NO_CASE_DIR, CASE_DIR, DEFAULT_BPE_CACHE_DIR

logger = logging.getLogger(__name__)

PARSED_FILE_EXTENSION = "parsed"
REPR_EXTENSION = "repr"
NOT_FINISHED_EXTENSION = "part"
READY_FILE = '.ready'

class ReprWriter(metaclass=ABCMeta):
    def __init__(self, dest_file, mode, extension):
        self.dest_file = dest_file
        self.mode = mode
        self.extension = extension

    def __enter__(self):
        self.handle = open(f'{self.get_full_dest_name()}.{NOT_FINISHED_EXTENSION}', self.mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.handle.close()

    def get_full_dest_name(self):
        return f'{self.dest_file}.{self.extension}'

    @abstractmethod
    def write(self, token_list):
        '''Has to be implemented by subclasses'''


class FinalReprWriter(ReprWriter):
    def __init__(self, dest_file):
        super().__init__(dest_file, 'w', f'{REPR_EXTENSION}')

    def write(self, token_list):
        self.handle.write(to_token_list(token_list))


def get_global_n_gramm_splitting_config():
    return global_n_gramm_splitting_config


def to_repr(prep_config: PrepConfig, token_list: List, n_gramm_splitting_config: Optional[NgramSplitConfig] = None):
    types_to_be_repr = get_types_to_be_repr(prep_config)
    splitting_config = n_gramm_splitting_config or get_global_n_gramm_splitting_config()
    dict_based_non_eng = (prep_config.get_param_value(PrepParam.EN_ONLY) != 3)
    lowercase = (prep_config.get_param_value(PrepParam.CAPS) == 1)
    repr_list = to_repr_list(token_list, ReprConfig(types_to_be_repr, splitting_config, dict_based_non_eng, lowercase))
    return repr_list


def preprocess_and_write(params):
    src_file, dest_file, prep_config = params
    if not os.path.exists(src_file):
        logger.error(f"File {src_file} does not exist")
        exit(2)

    logger.debug(f"Preprocessing parsed file {src_file}")
    with gzip.GzipFile(src_file, 'rb') as i:
        preprocessing_param_dict = pickle.load(i)
        writer = FinalReprWriter(dest_file)

        if os.path.exists(writer.get_full_dest_name()):
            logger.warning(f"File {writer.get_full_dest_name()} already exists! Doing nothing.")
            return
        with writer as w:
            while True:
                try:
                    token_list = pickle.load(i)
                    repr = to_repr(prep_config, token_list, global_n_gramm_splitting_config)
                    w.write(repr)
                except EOFError:
                    break
    # remove .part to show that all raw files in this chunk have been preprocessed
    os.rename(f'{writer.get_full_dest_name()}.{NOT_FINISHED_EXTENSION}', f'{writer.get_full_dest_name()}')


def init_splitting_config(prep_config: PrepConfig, bpe_n_merges: Optional[int]):
    global global_n_gramm_splitting_config
    global_n_gramm_splitting_config = NgramSplitConfig()
    if prep_config.get_param_value(PrepParam.SPLIT) in [4, 5, 6, 7, 8, 9]:

        if prep_config.get_param_value(PrepParam.SPLIT) == 9:
            if not bpe_n_merges:
                raise ValueError("--bpe-n-merges must be specified for repr **9**")
        else:
            bpe_n_merges_dict = {4: '5k', 5: '1k', 6: '10k', 7: '20k', 8: '0'}
            bpe_n_merges = bpe_n_merges_dict[prep_config.get_param_value(PrepParam.SPLIT)]

        logger.info(f'Using bpe_n_merges: {bpe_n_merges}')
        bpe_merges_file = os.path.join(DEFAULT_BPE_DIR,
                                          CASE_DIR if prep_config.get_param_value(PrepParam.CAPS) == 0 else NO_CASE_DIR,
                                          str(bpe_n_merges), 'merges.txt')
        bpe_merges_cache_file = os.path.join(DEFAULT_BPE_CACHE_DIR,
                                          CASE_DIR if prep_config.get_param_value(PrepParam.CAPS) == 0 else NO_CASE_DIR,
                                          str(bpe_n_merges), 'merges_cache.txt')
        if os.path.exists(bpe_merges_cache_file):
            global_n_gramm_splitting_config.merges_cache = read_dict_from_2_columns(bpe_merges_cache_file, val_type=list)
        else:
            global_n_gramm_splitting_config.merges_cache = {}
        global_n_gramm_splitting_config.merges = read_merges(bpe_merges_file)
        global_n_gramm_splitting_config.set_splitting_type(NgramSplittingType.BPE)
    elif prep_config.get_param_value(PrepParam.SPLIT) == 2:
        global_n_gramm_splitting_config.set_splitting_type(NgramSplittingType.ONLY_NUMBERS)


def mark_dir_as_ready(dir):
    open(os.path.join(dir, READY_FILE), 'a').close()


def check_dir_ready(dir):
    return os.path.exists(os.path.join(dir, READY_FILE))


def run(dataset: str, prep_config: PrepConfig, full_dest_dir: str, bpe_n_merges: Optional[int] = None):
    path_to_dataset = os.path.join(DEFAULT_PARSED_DATASETS_DIR, dataset)

    if not os.path.exists(path_to_dataset):
        logger.error(f"Dir does not exist: {path_to_dataset}")
        exit(3)
    logger.info(f"Reading parsed files from: {os.path.abspath(path_to_dataset)}")

    init_splitting_config(prep_config, bpe_n_merges)

    logger.info(f"Writing preprocessed files to {os.path.abspath(full_dest_dir)}")
    if not os.path.exists(full_dest_dir):
        os.makedirs(full_dest_dir)

    params = []
    for root, dirs, files in os.walk(path_to_dataset):
        for file in files:
            if file.endswith(f".{PARSED_FILE_EXTENSION}"):

                full_dest_dir_with_sub_dir = os.path.join(full_dest_dir, os.path.relpath(root, path_to_dataset))
                if not os.path.exists(full_dest_dir_with_sub_dir):
                    os.makedirs(full_dest_dir_with_sub_dir)
                params.append((os.path.join(root, file),
                               os.path.join(full_dest_dir_with_sub_dir, file),
                               prep_config))
    files_total = len(params)
    with Pool() as pool:
        it = pool.imap_unordered(preprocess_and_write, params)
        for _ in tqdm(it, total=files_total):
            pass
    mark_dir_as_ready(full_dest_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', action='store', help=f'path to the parsed dataset')
    parser.add_argument('repr', action='store', help='preprocessing params line, \n Example: 101011')
    parser.add_argument('full-dest-dir', action='store', help=f'TODO')
    parser.add_argument('--bpe-n-merges', action='store', type=int, help='TODO')

    args = parser.parse_known_args()
    args = args[0]

    run(args.dataset, PrepConfig.from_encoded_string(args.repr), args.full_dest_dir, args.bpe_n_merges)
