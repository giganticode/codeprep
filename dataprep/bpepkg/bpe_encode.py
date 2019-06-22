import logging
import sys

import argparse
from typing import List, Dict

from dataprep.bpepkg.merge import MergeList, read_merges

logger = logging.getLogger(__name__)


class BpeData(object):
    def __init__(self, merges_cache=None, merges: MergeList=None):
        self.merges_cache = merges_cache
        self.merges = merges


def encode(words: Dict[str, int], merges: MergeList) -> Dict[str, int]:
    letters_list = {" ".join(k): v for k, v in words.items()}

    new_letters_list = {}
    for letters, freq in letters_list.items():
        subwords = letters.split(" ")
        while True:
            merge_index = None
            merge_candidate_priority = sys.maxsize
            for i in range(len(subwords) - 1):
                merge_candidate = (subwords[i], subwords[i + 1])
                if merge_candidate in merges:
                    if merges.get_priority(merge_candidate) < merge_candidate_priority:
                        merge_candidate_priority = merges.get_priority(merge_candidate)
                        merge_index = i
            if merge_index is None:
                break
            concat_pair = ''.join([subwords[merge_index], subwords[merge_index + 1]])
            del subwords[merge_index]
            del subwords[merge_index]
            subwords = subwords[:merge_index] + [concat_pair] + subwords[merge_index:]
        new_letters_list[" ".join(subwords)] = freq
    return new_letters_list


def encode_word(word: str, merges: MergeList) -> List[str]:
    enc_word, _ = encode({word: 0}, merges).popitem()
    subwords = enc_word.split(" ")
    return subwords


def get_bpe_subwords(word: str, bpe_data: BpeData) -> List[str]:
    merges = bpe_data.merges
    cache = bpe_data.merges_cache
    if word in cache:
        return cache[word]
    else:
        return encode_word(word, merges)


__all__ = [encode, encode_word]


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('merges-file', action='store', help='path to file with merges')
    arg_parser.add_argument('word', action='store', help='word to encode', default='if')

    args = arg_parser.parse_args()

    merges = read_merges(args.merges_file)

    subwords = encode_word(args.word, merges)
    print(subwords)
