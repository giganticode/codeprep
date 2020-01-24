# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import collections
import logging

import regex
from tqdm import tqdm
from typing import Dict, List, Tuple, Set

from codeprep.bpepkg.merge import Merge, MergeList
from codeprep.util import PriorityCounter

logger = logging.getLogger(__name__)

# ======== BPE algo itself


def get_stats(split_base_vocab: Dict[str, int]) -> PriorityCounter:
    pairs = collections.defaultdict(int)
    for word, freq in split_base_vocab.items():
        symbols = word.split(' ')
        for i in range(len(symbols) - 1):
            pairs [symbols[i], symbols[i + 1]] += freq
    return PriorityCounter(pairs)


def merge_vocab(pair: Tuple[str, str], input_vocab: Dict[str, int]) -> Tuple[Dict[str, int], List]:
    """
    >>> pair = ('w', 'o')
    >>> input_vocab = {'b i r d @': 3, 'w o r d @': 7, 'w o g @': 13}
    >>> new_vocab, new_pairs = merge_vocab(pair, input_vocab)
    >>> new_vocab
    {'b i r d @': 3, 'wo r d @': 7, 'wo g @': 13}
    >>> new_pairs
    [(('wo', 'r'), 7), (('o', 'r'), -7), (('wo', 'g'), 13), (('o', 'g'), -13)]
    """
    output_vocab = {}
    concat_pair_with_space = ' '.join(pair)
    concat_pair_with_space_escaped = regex.escape(concat_pair_with_space)
    concat_pair = ''.join(pair)
    reg = regex.compile('(^|[^ ]+ )(' + concat_pair_with_space_escaped + ')( [^ ]+|$)')
    added_pairs = []
    for word in input_vocab:
        word_occurences = input_vocab[word]
        match = reg.search(word)
        while match:
            # word changed
            if match.group(1) != '':
                subtoken_before = match.group(1)[:-1]
                added_pairs.append(((subtoken_before, concat_pair), word_occurences))
                if pair != (subtoken_before, pair[0]):
                    added_pairs.append(((subtoken_before, pair[0]), -word_occurences))
            if match.group(3) != '':
                subtoken_after = match.group(3)[1:]
                added_pairs.append(((concat_pair, subtoken_after), word_occurences))
                if pair != (pair[1], subtoken_after):
                    added_pairs.append(((pair[1], subtoken_after), -word_occurences))
            start, end = match.span(2)
            replacement = concat_pair
            word = word[:start] + replacement + word[end:]
            match = reg.search(word)
        output_vocab[word] = word_occurences
    return output_vocab, added_pairs


def do_merges(vocab: Dict[str, int], n_merges: int) -> Tuple[Dict[str, int], MergeList]:
    """
    Do `n_merges` bpe merges starting from vocabulary splittings `vocab` which were formed after applying `already_done_merges` merges

    :param vocab: base vocab splittings formed after applying `already_done_merges` in a format
    {"fix me@": 3242, "a b c@": 400}
    :param n_merges: number of bpe merges to be applied
    :param already_done_merges: merges which has already been applied in a format ["e @, f i", "fi x", "m e@"]

    :return: a tuple where the first elements is the resulting vocab splittings,
    the second one are all the merges done to reach those vocab splittings

    >>> input_vocab = {
    ...     "b i r d @": 3,
    ...     "w o r d @": 7,
    ...     "w o g @": 13
    ... }

    >>> vocab, merges = do_merges(input_vocab, 10)
    >>> vocab
    {'bird@': 3, 'word@': 7, 'wog@': 13}
    >>> merges
    [('w', 'o'): (20, 0), ('g', '@'): (13, 1), ('wo', 'g@'): (13, 2), ('r', 'd'): (10, 3), ('rd', '@'): (10, 4), \
('wo', 'rd@'): (7, 5), ('b', 'i'): (3, 6), ('bi', 'rd@'): (3, 7)]


    >>> input_vocab = {"a a a a a @": 3}

    >>> do_merges(input_vocab, 10)
    ({'aaaaa@': 3}, [('a', 'a'): (12, 0), ('a', '@'): (3, 1), ('aa', 'aa'): (3, 2), ('aaaa', 'a@'): (3, 3)])

    >>> input_vocab = {"l a l a l a @": 3}
    >>> do_merges(input_vocab, 10)
    ({'lalala@': 3}, [('l', 'a'): (9, 0), ('la', 'la'): (6, 1), ('la', '@'): (3, 2), ('lala', 'la@'): (3, 3)])

    """
    merges = MergeList()
    pairs = get_stats(vocab)
    for i in tqdm(range(n_merges), total=n_merges):
        try:
            best, occurences = pairs.pop_pair()
            merges.append(Merge(best, freq=occurences, priority=i))
        except KeyError:
            break
        vocab, added_pairs = merge_vocab(best, vocab)
        for p in added_pairs:
            pairs.add(*p)
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