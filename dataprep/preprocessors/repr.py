import logging
from typing import List

from dataprep.split.ngram import NgramSplitConfig

logger = logging.getLogger(__name__)


class ReprConfig(object):
    def __init__(self, types_to_be_repr, ngram_split_config, dict_based_non_eng=True, should_lowercase=True):
        self.types_to_be_repr = types_to_be_repr
        self.ngram_split_config = ngram_split_config
        self.dict_based_non_eng = dict_based_non_eng
        self.should_lowercase = should_lowercase

    @classmethod
    def empty(cls):
        return cls([], NgramSplitConfig())


def to_repr_list(token_list, repr_config) -> List[str]:
    repr_res = []
    for token in token_list:
        repr_token = torepr(token, repr_config)
        repr_res.extend(repr_token)
    return repr_res


def torepr(token, repr_config) -> List[str]:
    clazz = type(token)
    if clazz.__name__ == 'ParseableToken':
        raise AssertionError(f"Parseable token cannot be present in the final parsed model: {token}")
    if clazz == list:
        return to_repr_list(token, repr_config)
    if clazz == str:
        return [token]

    if clazz in repr_config.types_to_be_repr:
        return token.preprocessed_repr(repr_config)
    else:
        non_prep = token.non_preprocessed_repr(repr_config)
        return non_prep if isinstance(non_prep, list) else [non_prep]
