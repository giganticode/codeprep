import logging
import os
from typing import Tuple, Dict, Set

from dataprep.bpepkg.bpe_config import BpeConfig, BpeParam, BpeConfigNotSupported
from dataprep.bpepkg.bpe_learn import separate_vocabs, logger, do_merges, create_resulting_vocab, create_bpe_cache
from dataprep.bpepkg.cache import dump_bpe_cache
from dataprep.bpepkg.merge import MergeList, read_merges, dump_merges
from dataprep.infrastructure import stages
from dataprep.infrastructure.bperegistry import get_max_merges, MERGES_FILE_NAME, MERGES_CACHE_FILE_NAME, \
    RESULTING_VOCAB_FILE_NAME, BPE_REASSEMBLED_VOCAB_FILE_NAME
from dataprep.infrastructure.dataset import Dataset
from dataprep.vocab import _dump_vocab_dict, _load_vocab_dict


def get_base_vocab(dataset: Dataset) -> Tuple[Dict[str, int], Dict[str, int]]:
    stages.run_until_base_bpe_vocab(dataset)
    all_vocab = _load_vocab_dict(dataset.path_to_bpe_vocab_file)
    non_bpe_vocab = load_nonbpe_vocab(dataset)
    return separate_vocabs(all_vocab, non_bpe_vocab)


def load_nonbpe_vocab(dataset: Dataset) -> Set[str]:
    non_bpe_vocab = set()
    with open(dataset.path_to_nonbpe_vocab_file, 'r') as f:
        for line in f:
            non_bpe_vocab.add(line.rstrip('\n'))
    return non_bpe_vocab


def check_if_bpe_config_supported(bpe_config: BpeConfig):
    if bpe_config.get_param_value(BpeParam.UNICODE) == 'bytes':
        raise BpeConfigNotSupported('Byte-BPE is not yet supported')

    if bpe_config.get_param_value(BpeParam.WORD_END):
        raise BpeConfigNotSupported('BPE with word-end characters are not yet supported')

    if bpe_config.get_param_value(BpeParam.CASE) == 'prefix':
        raise BpeConfigNotSupported('BPE with case encoded in prefix is not yet supported')


def run(dataset: Dataset, n_merges: int, bpe_config: BpeConfig) -> None:

    check_if_bpe_config_supported(bpe_config)

    max_merges = get_max_merges(dataset.bpe_path, n_merges)
    if not max_merges:
        starting_from_scratch = True
    else:
        dir_with_most_merges = os.path.join(dataset.bpe_path, str(max_merges))
        starting_from_scratch = False
        logger.info("Using existing mexrges...")

    if starting_from_scratch:
        logger.info("Starting encoding from scratch...")

    if starting_from_scratch:
        base_bpe_vocab, other_vocab = get_base_vocab(dataset) #TODO extract this into stages
        split_base_vocab = {" ".join(k): v for k, v in base_bpe_vocab.items()}
        already_done_merges = MergeList()
    else:
        path_to_bpe_vocab_file = os.path.join(dir_with_most_merges, BPE_REASSEMBLED_VOCAB_FILE_NAME)
        split_base_vocab = _load_vocab_dict(path_to_bpe_vocab_file)
        split_base_vocab, other_vocab = separate_vocabs(split_base_vocab, load_nonbpe_vocab(dataset))
        already_done_merges = read_merges(os.path.join(dir_with_most_merges, MERGES_FILE_NAME))

    logger.info("Learning bpe codes...")
    split_base_vocab, merges = do_merges(split_base_vocab, n_merges-len(already_done_merges))
    merges = already_done_merges + merges

    new_bpe_dir = os.path.join(dataset.bpe_path, str(len(merges)))
    if os.path.exists(new_bpe_dir):
        logging.info("Merges already learned!")
        return

    os.makedirs(new_bpe_dir)

    for k, v in other_vocab.items():
        split_base_vocab[k] = v

    resulting_vocab = create_resulting_vocab(split_base_vocab)
    resulting_vocab_sorted = sorted(resulting_vocab.items(), key=lambda x: x[1], reverse=True)
    _dump_vocab_dict(resulting_vocab_sorted, os.path.join(new_bpe_dir, RESULTING_VOCAB_FILE_NAME))

    bpe_cache = create_bpe_cache(split_base_vocab)
    dump_bpe_cache(bpe_cache, os.path.join(new_bpe_dir, MERGES_CACHE_FILE_NAME))

    dump_merges(merges, os.path.join(new_bpe_dir, MERGES_FILE_NAME))
    _dump_vocab_dict(split_base_vocab.items(), os.path.join(new_bpe_dir, BPE_REASSEMBLED_VOCAB_FILE_NAME))
    logger.info(f'Bpe output files are saved into {new_bpe_dir} folder')