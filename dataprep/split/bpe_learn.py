import argparse
import logging
import os
import re, collections
from tqdm import tqdm
from typing import Optional, Dict, List, Tuple


from dataprep import util
from dataprep.bperegistry import get_max_merges, MERGES_CACHE_FILE_NAME, MERGES_FILE_NAME
from dataprep.cli import stages
from dataprep.dataset import Dataset
from dataprep.model.placeholders import placeholders
from dataprep.preprocessors.java import special_tokens
from dataprep.split.bpe_config import BpeConfig, BpeParam
from dataprep.util import PriorityCounter, read_dict_from_2_columns, read_list, dump_dict_into_2_columns, dump_list

logger = logging.getLogger(__name__)

OTHER_VOCAB_FILE_NAME = "other_vocab"
BPE_REASSEMBLED_VOCAB_FILE_NAME = "bpe_vocab_reassembled.txt"
RESULTING_VOCAB_FILE_NAME = "vocab_res.txt"

# ======== BPE algo itself


def get_stats(split_base_vocab: Dict[str, int]) -> PriorityCounter:
    pairs = collections.defaultdict(int)
    for word, freq in split_base_vocab.items():
        symbols = word.split()
        for i in range(len(symbols) - 1):
            pairs [symbols[i], symbols[i + 1]] += freq
    return PriorityCounter(pairs)


def merge_vocab(pair: Tuple[str, str], input_vocab: Dict[str, int], pairs: PriorityCounter) -> Dict[str, int]:
    output_vocab = {}
    concat_pair_with_space = ' '.join(pair)
    concat_pair_with_space_escaped = re.escape(concat_pair_with_space)
    concat_pair = ''.join(pair)
    reg = re.compile('(^|\S+ )(' + concat_pair_with_space_escaped + ')( \S+|$)')
    for word in input_vocab:
        word_occurences = input_vocab[word]
        match = reg.search(word)
        while match:
            # word changed
            if match.group(1) != '':
                subtoken_before = match.group(1)[:-1]
                pairs.add((subtoken_before, concat_pair), word_occurences)
                if pair != (subtoken_before, pair[0]):
                    pairs.add((subtoken_before, pair[0]), -word_occurences)
            if match.group(3) != '':
                subtoken_after = match.group(3)[1:]
                pairs.add((concat_pair, subtoken_after), word_occurences)
                if pair != (pair[1], subtoken_after):
                    pairs.add((pair[1], subtoken_after), -word_occurences)
            start, end = match.span(2)
            replacement = repr(concat_pair)[1:-1]
            word = word[:start] + replacement + word[end:]
            match = reg.search(word)
        output_vocab[word] = word_occurences
    return output_vocab


def do_merges(vocab: Dict[str, int], n_merges: int) -> Tuple[Dict[str, int], List[Tuple[str, str, int]]]:
    """
    Do `n_merges` bpe merges starting from vocabulary splittings `vocab` which were formed after applying `already_done_merges` merges

    :param vocab: base vocab splittings formed after applying `already_done_merges` in a format
    {"fix me": 3242, "a b c": 400}
    :param n_merges: number of bpe merges to be applied
    :param already_done_merges: merges which has already been applied in a format ["f i", "fi x", "m e"]

    :return: a tuple where the first elements is the resulting vocab splittings,
    the second one are all the merges done to reach those vocab splittings
    """
    merges = []
    pairs = get_stats(vocab)
    for i in tqdm(range(n_merges), total=n_merges):
        try:
            best, occurences = pairs.pop_pair()
            merges.append((best[0], best[1], occurences))
        except KeyError:
            break
        vocab = merge_vocab(best, vocab, pairs)
    return vocab, merges


def separate_non_splittable_vocab(all_vocab: Dict[str, int], from_reassambled: bool) -> (Dict[str, int], Dict[str, int]):
    vocab = {}
    non_splitable_vocab = {}
    for k, v in all_vocab.items():
        placeholders_values = placeholders.values()
        if k not in placeholders_values and k not in special_tokens:
            vocab[k if from_reassambled else " ".join(k)] = v
        else:
            non_splitable_vocab[k] = v
    return vocab, non_splitable_vocab

# ======== Create auxiliary data structures.


def create_bpe_cache(vocab: Dict[str, int]) -> Dict[str, List[str]]:
    merges_cache = {}
    for entry, _ in vocab.items():
        subword_list = entry.split(' ')
        key = ''.join(subword_list)
        merges_cache[key] = subword_list
    return merges_cache


def create_resulting_vocab(split_base_vocab: Dict[str, int]) -> Dict[str, int]:
    resulting_vocab = collections.defaultdict(int)
    for entry, frequency in split_base_vocab.items():
        for subword in entry.split(" "):
            resulting_vocab[subword] += frequency
    return resulting_vocab

# ============


def separate_vocabs(all_vocab: Dict[str, int], tokens_to_exclude: Dict[str, int]) -> Tuple[Dict[str, int], Dict[str, int]]:
    main_vocab = {}
    other_vocab = {}
    for k, v in all_vocab.items():
        if k not in tokens_to_exclude:
            main_vocab[k] = v
        else:
            other_vocab[k] = v
    return main_vocab, other_vocab


def get_base_vocab(dataset: Dataset, bpe_config: BpeConfig) -> Tuple[Dict[str, int], Dict[str, int]]:
    stages.run_until_vocab(dataset)
    all_vocab = util.read_dict_from_2_columns(dataset.path_to_bpe_vocab_file)
    tokens_to_exclude_from_bpe =  special_tokens + list(placeholders.keys()) if bpe_config.get_param_value(BpeParam.BASE) == 'java' \
        else list(placeholders.keys())
    return separate_vocabs(all_vocab, tokens_to_exclude_from_bpe)


def run(dataset: Dataset, n_merges: int, bpe_config: BpeConfig) -> None:

    max_merges = get_max_merges(dataset.bpe_path, n_merges)
    if not max_merges:
        starting_from_scratch = True
    else:
        dir_with_most_merges = os.path.join(dataset.bpe_path, str(max_merges))
        starting_from_scratch = False
        logger.info("Using existing mexrges...")

    if starting_from_scratch:
        logger.info("Starting the encoding from scratch...")

    if starting_from_scratch:
        if not os.path.exists(dataset.path_to_bpe_vocab_file):
            base_bpe_vocab, other_vocab = get_base_vocab(dataset, bpe_config) #TODO extract this into stages
            split_base_vocab = {" ".join(k): v for k, v in base_bpe_vocab.items()}
            # TODO dump to vocab and other vocab files
        already_done_merges = []
    else:
        path_to_bpe_vocab_file = os.path.join(dir_with_most_merges, BPE_REASSEMBLED_VOCAB_FILE_NAME)
        split_base_vocab = read_dict_from_2_columns(path_to_bpe_vocab_file)
        split_base_vocab, other_vocab = separate_vocabs(split_base_vocab, special_tokens + list(placeholders.keys()))
        already_done_merges = read_list(os.path.join(dir_with_most_merges, MERGES_FILE_NAME))

    print("--- Learning bpe codes...")
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
    dump_dict_into_2_columns(resulting_vocab_sorted, os.path.join(new_bpe_dir, RESULTING_VOCAB_FILE_NAME))

    bpe_cache = create_bpe_cache(split_base_vocab)
    dump_dict_into_2_columns(bpe_cache, os.path.join(new_bpe_dir, MERGES_CACHE_FILE_NAME), val_type=list)

    dump_list(merges, os.path.join(new_bpe_dir, MERGES_FILE_NAME))
    dump_dict_into_2_columns(split_base_vocab, os.path.join(new_bpe_dir, BPE_REASSEMBLED_VOCAB_FILE_NAME))
    logger.info(f'Bpe output files are saved into {new_bpe_dir} folder')


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('path_to_dataset', action='store', help=f'dataset name')
    argument_parser.add_argument('n_merges', action='store', type=int)

    args = argument_parser.parse_args()

    run(args.path_to_dataset, None, args.n_merges, args.reset, BpeConfig())
