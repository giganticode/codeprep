from enum import Enum, auto
from typing import List

from dataprep.split.bpe_encode import encode_word



class NgramSplittingType(Enum):
    BPE = auto()
    ONLY_NUMBERS = auto()


class NgramSplitConfig(object):
    def __init__(self, splitting_type=None, merges_cache=None, merges=None):
        self._splitting_type = splitting_type
        self._merges_cache = merges_cache
        self._merges = merges

    @property
    def merges_cache(self):
        return self._merges_cache

    @property
    def merges(self):
        return self._merges

    @merges.setter
    def merges(self, m):
        self._merges = m

    @merges_cache.setter
    def merges_cache(self, m):
        self._merges_cache = m

    def set_splitting_type(self, type):
        self._splitting_type = type

    @property
    def splitting_type(self):
        return self._splitting_type


def get_bpe_subwords(word, config) -> List[str]:
    merges = config.merges
    cache = config.merges_cache
    if word in cache:
        return cache[word]
    else:
        return encode_word(word, merges)


def do_ngram_splitting(token, ngram_split_config):
    if ngram_split_config.splitting_type and ngram_split_config.splitting_type == NgramSplittingType.BPE:
        subwords = get_bpe_subwords(token, ngram_split_config)
    else:
        subwords = [token]

    return subwords
