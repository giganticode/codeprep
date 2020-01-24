# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import sys

import argparse
from typing import List, Dict

from tqdm import tqdm

from codeprep.bpepkg.merge import MergeList, read_merges
from codeprep.config import DEFAULT_BPE_DIR

logger = logging.getLogger(__name__)


class BpeData(object):
    def __init__(self, merges_cache=None, merges: MergeList=None):
        self.merges_cache = merges_cache
        self.merges = merges


ESCAPE_CHAR = '@'

ESCAPABLE_CHAR_LIST = [] + [ESCAPE_CHAR]


def escape(word: str, merged: bool=False) -> str:
    word = word.replace(ESCAPE_CHAR, 2 * ESCAPE_CHAR)
    if merged:
        return f"{word}{ESCAPE_CHAR}"
    else:
        return f"{word} {ESCAPE_CHAR}"


def unescape(parts: List[str]):
    if parts[-1][-1] != ESCAPE_CHAR:
        raise ValueError(f"There should be {ESCAPE_CHAR} at the end, however this is what was passed: {parts}")

    parts[-1] = parts[-1][:-1]
    return list(map(lambda p: p.replace(ESCAPE_CHAR + '@', ESCAPE_CHAR), parts))


def to_char_list(word: str):
    i = 0
    res = []
    while i < len(word):
        if word[i] != ESCAPE_CHAR or i+1 == len(word):
            res.append(word[i])
            i += 1
        elif word[i+1] in ESCAPABLE_CHAR_LIST:
            res.append(word[i:i+2])
            i += 2
        else:
            raise ValueError(f"Illegal escape sequence: {word[i:i+2]}")
    return res


def encode(words: Dict[str, int], merges: MergeList) -> Dict[str, int]:
    letters_list = {" ".join(to_char_list(k)): v for k, v in words.items()}

    new_letters_list = {}
    for letters, freq in letters_list.items():
        subwords = letters.split(" ")

        show_bpe_progress_bar = False
        if len(subwords) > 5000:
            logger.warning(f'Encountered a string of length {len(subwords)}. It will take a while to bpe-encode it.')
            show_bpe_progress_bar = True

        if show_bpe_progress_bar:
            bpe_progress = tqdm(total=len(merges))
            last_value = 0
        while True:
            merge_indices = []
            merge_candidate_priority = sys.maxsize
            for i in range(len(subwords) - 1):
                merge_candidate = (subwords[i], subwords[i + 1])
                if merge_candidate in merges:
                    current_merge_candidate_priority = merges.get_priority(merge_candidate)
                    if current_merge_candidate_priority < merge_candidate_priority:
                        merge_candidate_priority = current_merge_candidate_priority
                        merge_indices = [i]
                    elif current_merge_candidate_priority == merge_candidate_priority:
                        if not merge_indices or merge_indices[-1] != i - 1:
                            merge_indices.append(i)

            if not merge_indices:
                break

            subwords_after_this_merge_round = []
            start_idx = 0
            for merge_index in merge_indices:
                for i in range(start_idx, merge_index):
                    subwords_after_this_merge_round.append(subwords[i])
                subwords_after_this_merge_round.append(subwords[merge_index] + subwords[merge_index + 1])
                start_idx = merge_index + 2
            for i in range(start_idx, len(subwords)):
                subwords_after_this_merge_round.append(subwords[i])
            subwords = subwords_after_this_merge_round
            if show_bpe_progress_bar:
                bpe_progress.update(merge_candidate_priority - last_value)
                last_value = merge_candidate_priority
        if show_bpe_progress_bar:
            bpe_progress.update(len(merges) - last_value)
            bpe_progress.close()

        new_letters_list[" ".join(subwords)] = freq
    return new_letters_list


def encode_word(word: str, merges: MergeList) -> List[str]:
    """
    >>> merge_file = os.path.join(DEFAULT_BPE_DIR, '10k', 'merges.txt')
    >>> merges = read_merges(merge_file, 10000)

    >>> encode_word('this@@is_all_one_String@', merges)
    ['this', '@@', 'is_', 'all', '_', 'one', '_', 'String@']

    >>> encode_word('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa@', merges)
    ['aaaaaaaa', 'aaaaaaaa', 'aaaaaaaa', 'aaaaaaaa', 'aaaa', 'a', 'a@']

    >>> encode_word('erererererererererererer@', merges)
    ['er', 'er', 'er', 'er', 'er', 'er', 'er', 'er', 'er', 'er', 'er', 'er@']

    >>> encode_word('@', merges)
    ['@']

    >>> encode_word('', merges)
    ['']

    >>> encode_word('split@', merges)
    ['split@']

    >>> encode_word('aaa', merges)
    ['aa', 'a']

    >>> encode_word('this\xa0is@@a@@@@bit@@@@larger\xa0stringwith\xa0some@@unicode@@possibly\xf7@', merges)
    ['this', '\\xa0', 'is', '@@', 'a', '@@', '@@', 'bit', '@@', '@@', 'l', 'arg', 'er', '\\xa0', 'string', \
'with', '\\xa0', 's', 'ome', '@@', 'unic', 'ode', '@@', 'pos', 'si', 'b', 'ly', '÷', '@']
    """
    enc_word, _ = encode({word: 0}, merges).popitem()
    subwords = enc_word.split(" ")
    return subwords


def get_bpe_subwords(word: str, bpe_data: BpeData) -> List[str]:
    merges = bpe_data.merges
    cache = bpe_data.merges_cache
    word = escape(word, merged=True)
    if word in cache:
        result = cache[word]
    else:
        result = encode_word(word, merges)

    return unescape(result)


__all__ = [encode, encode_word]


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('merges-file', action='store', help='path to file with merges')
    arg_parser.add_argument('word', action='store', help='word to encode', default='if')

    args = arg_parser.parse_args()

    merges = read_merges(args.merges_file)

    subwords = encode_word(args.word, merges)
    print(subwords)