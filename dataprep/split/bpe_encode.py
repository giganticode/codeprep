import argparse
import logging
import sys
from typing import List, Optional, Dict, Tuple

logger = logging.getLogger(__name__)

def encode(words, merges):
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
                    if merges[merge_candidate] < merge_candidate_priority:
                        merge_candidate_priority = merges[merge_candidate]
                        merge_index = i
            if merge_index is None:
                break
            concat_pair = ''.join([subwords[merge_index], subwords[merge_index + 1]])
            del subwords[merge_index]
            del subwords[merge_index]
            subwords = subwords[:merge_index] + [concat_pair] + subwords[merge_index:]
        new_letters_list[" ".join(subwords)] = freq
    return new_letters_list


def read_merges(merges_file: str, n_merges: Optional[int]=None) -> Dict[Tuple[str, str], int]:
    merges = {}
    with open(merges_file, 'r') as f:
        for idx, line in enumerate(f):
            if n_merges and idx >= n_merges:
                break
            line = line.rstrip('\n')
            merges[tuple(line.split(" ")[:2])] = idx
    return merges


def encode_word(word, merges) -> List[str]:
    enc_word, _ = encode({word: 0}, merges).popitem()
    subwords = enc_word.split(" ")
    return subwords


__all__ = [read_merges, encode_word]


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('merges-file', action='store', help='path to file with merges')
    arg_parser.add_argument('word', action='store', help='word to encode', default='if')

    args = arg_parser.parse_args()

    merges = read_merges(args.merges_file)

    subwords = encode_word(args.word, merges)
    print(subwords)
