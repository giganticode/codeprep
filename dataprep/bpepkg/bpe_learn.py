import collections
import logging

import regex
from tqdm import tqdm
from typing import Dict, List, Tuple, Set

from dataprep.bpepkg.merge import Merge, MergeList
from dataprep.util import PriorityCounter

logger = logging.getLogger(__name__)

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
    concat_pair_with_space_escaped = regex.escape(concat_pair_with_space)
    concat_pair = ''.join(pair)
    reg = regex.compile('(^|\S+ )(' + concat_pair_with_space_escaped + ')( \S+|$)')
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


def do_merges(vocab: Dict[str, int], n_merges: int) -> Tuple[Dict[str, int], MergeList]:
    """
    Do `n_merges` bpe merges starting from vocabulary splittings `vocab` which were formed after applying `already_done_merges` merges

    :param vocab: base vocab splittings formed after applying `already_done_merges` in a format
    {"fix me": 3242, "a b c": 400}
    :param n_merges: number of bpe merges to be applied
    :param already_done_merges: merges which has already been applied in a format ["f i", "fi x", "m e"]

    :return: a tuple where the first elements is the resulting vocab splittings,
    the second one are all the merges done to reach those vocab splittings
    """
    merges = MergeList()
    pairs = get_stats(vocab)
    for i in tqdm(range(n_merges), total=n_merges):
        try:
            best, occurences = pairs.pop_pair()
            merges.append(Merge(best, freq=occurences, priority=i))
        except KeyError:
            break
        vocab = merge_vocab(best, vocab, pairs)
    return vocab, merges

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


def separate_vocabs(all_vocab: Dict[str, int], tokens_to_exclude: Set[str]) -> Tuple[Dict[str, int], Dict[str, int]]:
    main_vocab = {}
    other_vocab = {}
    for k, v in all_vocab.items():
        if k not in tokens_to_exclude:
            main_vocab[k] = v
        else:
            other_vocab[k] = v
    return main_vocab, other_vocab
