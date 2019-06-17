import gzip
import logging
import os
import pickle

import time
from multiprocessing.pool import Pool
from tqdm import tqdm
from typing import List, Tuple, Generator, Union
from typing import Optional

from dataprep.bpepkg.bpe_encode import read_merges
from dataprep.bpepkg.bperegistry import CustomBpeConfig
from dataprep.bpepkg.cache import read_bpe_cache
from dataprep.config import DEFAULT_BPE_DIR, NO_CASE_DIR, CASE_DIR, DEFAULT_BPE_CACHE_DIR, REWRITE_PREPROCESSED_FILE, \
    CHUNKSIZE, LIMIT_FILES_SCANNING
from dataprep.dataset import Dataset, NOT_FINISHED_EXTENSION
from dataprep.model.core import ParsedToken
from dataprep.model.metadata import PreprocessingMetadata
from dataprep.model.metadata import save_metadata
from dataprep.model.placeholders import placeholders
from dataprep.prepconfig import PrepParam, get_types_to_be_repr, PrepConfig
from dataprep.preprocess.core import ReprConfig, to_repr_list
from dataprep.split.ngram import NgramSplitConfig
from dataprep.split.ngram import NgramSplittingType
from dataprep.vocab import vocabloader

logger = logging.getLogger(__name__)


def get_global_n_gramm_splitting_config():
    return global_n_gramm_splitting_config


def to_repr(prep_config: PrepConfig, token_list: List[Union[str, ParsedToken]],
            n_gramm_splitting_config: Optional[NgramSplitConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
    types_to_be_repr = get_types_to_be_repr(prep_config)
    splitting_config = n_gramm_splitting_config or get_global_n_gramm_splitting_config()
    dict_based_non_eng = (prep_config.get_param_value(PrepParam.EN_ONLY) != 3)
    lowercase = (prep_config.get_param_value(PrepParam.CAPS) == 1)
    repr_list, metadata = to_repr_list(token_list, ReprConfig(types_to_be_repr, splitting_config, dict_based_non_eng, lowercase))
    return repr_list, metadata


def to_token_str(tokens: List) -> str:
    return repr(" ".join(map(lambda t : str(t),tokens)))[1:-1] + f" {placeholders['ect']}\n"


def preprocess_and_write(params: Tuple[bytes, bytes, PrepConfig, str]):
    src_file_path, dest_file_path, prep_config, part_nonbpe_vocab_folder = params

    dest_dirname = os.path.dirname(dest_file_path)
    if not os.path.exists(dest_dirname):
        os.makedirs(dest_dirname, exist_ok=True)

    if not REWRITE_PREPROCESSED_FILE and os.path.exists(dest_file_path):
        logger.warning(f"File {dest_file_path} already exists! Doing nothing.")
        return

    not_finished_dest_file_path = dest_file_path + NOT_FINISHED_EXTENSION.encode()
    with gzip.GzipFile(src_file_path, 'rb') as i, open(not_finished_dest_file_path, 'w') as o:
        token_list = pickle.load(i)
        repr, metadata = to_repr(prep_config, token_list, global_n_gramm_splitting_config)
        o.write(to_token_str(repr))

    if part_nonbpe_vocab_folder:
        save_metadata(metadata, os.path.join(part_nonbpe_vocab_folder, f'{os.path.basename(dest_file_path)}_-_{time.time()}'))

    os.rename(not_finished_dest_file_path, dest_file_path)


def init_splitting_config(prep_config: PrepConfig, custom_bpe_config: Optional[CustomBpeConfig]):
    global global_n_gramm_splitting_config
    global_n_gramm_splitting_config = NgramSplitConfig()
    if prep_config.get_param_value(PrepParam.SPLIT) in [4, 5, 6, 7, 8, 9]:
        if custom_bpe_config:
            logger.info(f'Using bpe merges file: {custom_bpe_config.codes_file}')
            if custom_bpe_config.can_use_cache_file():
                global_n_gramm_splitting_config.merges_cache = read_bpe_cache(custom_bpe_config.cache_file)
            else:
                global_n_gramm_splitting_config.merges_cache = {}
            global_n_gramm_splitting_config.merges = read_merges(custom_bpe_config.codes_file, custom_bpe_config.n_merges)

            if custom_bpe_config.n_merges:
                logger.info(f'Using first {custom_bpe_config.n_merges} merges.')
            nonbpe_vocab = vocabloader.nonbpe(custom_bpe_config.id)
            global_n_gramm_splitting_config.merges_cache.update({s: [s] for s in nonbpe_vocab})
        else:
            bpe_n_merges_dict = {4: '5k', 5: '1k', 6: '10k', 7: '20k', 8: '0'}
            bpe_n_merges = bpe_n_merges_dict[prep_config.get_param_value(PrepParam.SPLIT)]

            bpe_merges_file = os.path.join(DEFAULT_BPE_DIR,
                                              CASE_DIR if prep_config.get_param_value(PrepParam.CAPS) == 0 else NO_CASE_DIR,
                                              str(bpe_n_merges), 'merges.txt')
            bpe_merges_cache_file = os.path.join(DEFAULT_BPE_CACHE_DIR,
                                              CASE_DIR if prep_config.get_param_value(PrepParam.CAPS) == 0 else NO_CASE_DIR,
                                              str(bpe_n_merges), 'merges_cache.txt')
            if os.path.exists(bpe_merges_cache_file):
                global_n_gramm_splitting_config.merges_cache = read_bpe_cache(bpe_merges_cache_file)
            else:
                global_n_gramm_splitting_config.merges_cache = {}
            global_n_gramm_splitting_config.merges = read_merges(bpe_merges_file)
        global_n_gramm_splitting_config.set_splitting_type(NgramSplittingType.BPE)
    elif prep_config.get_param_value(PrepParam.SPLIT) == 2:
        global_n_gramm_splitting_config.set_splitting_type(NgramSplittingType.ONLY_NUMBERS)
    elif prep_config.get_param_value(PrepParam.SPLIT) == 3:
        global_n_gramm_splitting_config.set_splitting_type(NgramSplittingType.RONIN)


def params_generator(dataset: Dataset):
    path_to_nonbpe_vocab_folder = f'{dataset.path_to_nonbpe_vocab_file}_part' if not os.path.exists(dataset.path_to_nonbpe_vocab_file) else None
    for input_file_path in dataset.parsed.file_iterator():
        output_file_path = dataset.parsed.get_new_file_name(input_file_path, dataset.preprocessed)
        yield (input_file_path, output_file_path, dataset.prep_config, path_to_nonbpe_vocab_folder)


def run(dataset: Dataset, custom_bpe_config: Optional[CustomBpeConfig]) -> None:
    path_to_parsed_dataset = dataset.parsed.path

    if not os.path.exists(path_to_parsed_dataset):
        logger.error(f"Dir does not exist: {path_to_parsed_dataset}")
        exit(3)
    logger.info(f"Reading parsed files from: {path_to_parsed_dataset}")

    init_splitting_config(dataset.prep_config, custom_bpe_config)

    nonbpe_vocab_part_folder = f'{dataset.path_to_nonbpe_vocab_file}_part'
    if not os.path.exists(nonbpe_vocab_part_folder) and not os.path.exists(dataset.path_to_nonbpe_vocab_file):
        os.makedirs(nonbpe_vocab_part_folder)

    logger.info(f"Writing preprocessed files to {dataset.preprocessed.path}")

    if dataset.files_need_to_be_saved():
        files_total = 0
        for _ in dataset.get_all_files():
            files_total += 1
            print(f"Files scanned: {files_total}", end='\r')
            if files_total > LIMIT_FILES_SCANNING:
                files_total = None
                print(f"Total files to be preprocessed: {LIMIT_FILES_SCANNING}+")
                break
    else:
        files_total = len([f for f in dataset.get_all_files()])
    with Pool() as pool:
        it = pool.imap_unordered(preprocess_and_write, params_generator(dataset), chunksize=CHUNKSIZE)
        for _ in tqdm(it, total=files_total):
            pass

    if not os.path.exists(dataset.path_to_nonbpe_vocab_file):
        vocabloader.gather_non_bpe_vocab(dataset)

    dataset.preprocessed.set_ready()
