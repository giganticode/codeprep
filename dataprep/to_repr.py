import gzip
import logging
import os
import pickle
from multiprocessing.pool import Pool
from typing import Optional, List, Tuple, Iterator

from tqdm import tqdm

from dataprep.dataset import Dataset, NOT_FINISHED_EXTENSION
from dataprep.prepconfig import PrepParam, get_types_to_be_repr, PrepConfig
from dataprep.preprocessors.general import to_token_str
from dataprep.preprocessors.repr import to_repr_list, ReprConfig
from dataprep.split.bpe_encode import read_merges
from dataprep.split.ngram import NgramSplittingType, NgramSplitConfig
from dataprep.util import read_dict_from_2_columns
from dataprep.config import DEFAULT_BPE_DIR, NO_CASE_DIR, CASE_DIR, DEFAULT_BPE_CACHE_DIR, REWRITE_PREPROCESSED_FILE, \
    CHUNKSIZE

logger = logging.getLogger(__name__)


def get_global_n_gramm_splitting_config():
    return global_n_gramm_splitting_config


def to_repr(prep_config: PrepConfig, token_list: List, n_gramm_splitting_config: Optional[NgramSplitConfig] = None) -> List[str]:
    types_to_be_repr = get_types_to_be_repr(prep_config)
    splitting_config = n_gramm_splitting_config or get_global_n_gramm_splitting_config()
    dict_based_non_eng = (prep_config.get_param_value(PrepParam.EN_ONLY) != 3)
    lowercase = (prep_config.get_param_value(PrepParam.CAPS) == 1)
    repr_list = to_repr_list(token_list, ReprConfig(types_to_be_repr, splitting_config, dict_based_non_eng, lowercase))
    return repr_list


def preprocess_and_write(params: Tuple[bytes, bytes, PrepConfig]):
    src_file_path, dest_file_path, prep_config = params

    dest_dirname = os.path.dirname(dest_file_path)
    if not os.path.exists(dest_dirname):
        os.makedirs(dest_dirname, exist_ok=True)

    if not REWRITE_PREPROCESSED_FILE and os.path.exists(dest_file_path):
        logger.warning(f"File {dest_file_path} already exists! Doing nothing.")
        return

    not_finished_dest_file_path = dest_file_path + NOT_FINISHED_EXTENSION.encode()
    with gzip.GzipFile(src_file_path, 'rb') as i, open(not_finished_dest_file_path, 'w') as o:
        token_list = pickle.load(i)
        repr = to_repr(prep_config, token_list, global_n_gramm_splitting_config)
        o.write(to_token_str(repr))

    os.rename(not_finished_dest_file_path, dest_file_path)


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


def params_generator(dataset: Dataset):
    for input_file_path in dataset.parsed.file_iterator_from_file():
        output_file_path = dataset.parsed.get_new_file_name(input_file_path, dataset.preprocessed)
        yield (input_file_path, output_file_path, dataset.prep_config)


def exception_handler(it: Iterator):
    while True:
        try:
            yield next(it)
        except StopIteration:
            return
        except Exception as err:
            logger.error(f"{err}. Ignoring...")


def run(dataset: Dataset, bpe_n_merges: Optional[int] = None):
    path_to_parsed_dataset = dataset.parsed.path

    if not os.path.exists(path_to_parsed_dataset):
        logger.error(f"Dir does not exist: {path_to_parsed_dataset}")
        exit(3)
    logger.info(f"Reading parsed files from: {path_to_parsed_dataset}")

    init_splitting_config(dataset.prep_config, bpe_n_merges)

    logger.info(f"Writing preprocessed files to {dataset.preprocessed.path}")

    files_total = len([f for f in dataset.get_all_files()])
    with Pool() as pool:
        it = pool.imap_unordered(preprocess_and_write, params_generator(dataset), chunksize=CHUNKSIZE)
        for _ in tqdm(exception_handler(it), total=files_total):
            pass
    dataset.preprocessed.set_ready()
