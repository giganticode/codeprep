from typing import Tuple, List, Optional, Callable, Sequence

from dataprep.bpepkg.bpe_encode import BpeData
from dataprep.preprocess.metadata import PreprocessingMetadata
from dataprep.tokens.rootclasses import ParsedToken

Splitter = Callable[[str, BpeData], List[str]]


class ReprConfig(object):
    def __init__(self, types_to_be_repr,
                 bpe_data: Optional[BpeData],
                 should_lowercase: bool,
                 number_splitter: Splitter,
                 word_splitter: Optional[Splitter],
                 full_strings: bool,
                 max_str_length: int):
        self.types_to_be_repr = types_to_be_repr
        self.bpe_data = bpe_data
        self.should_lowercase = should_lowercase
        self.number_splitter = number_splitter
        self.word_splitter = word_splitter
        self.full_strings = full_strings
        self.max_str_length = max_str_length


def to_repr_list(token_list: Sequence[ParsedToken], repr_config: ReprConfig) \
        -> Tuple[List[str], PreprocessingMetadata]:
    repr_res = []
    all_metadata = PreprocessingMetadata()
    for token in token_list:
        repr_token, metadata = torepr(token, repr_config)
        repr_res.extend(repr_token)
        all_metadata.update(metadata)
    return repr_res, all_metadata


def torepr(token, repr_config) -> Tuple[List[str], PreprocessingMetadata]:
    clazz = type(token)
    if clazz == str:
        raise AssertionError('Strings are not allowed any more as a result of parsing')
    if clazz == list:
        return to_repr_list(token, repr_config)
    if repr_config and clazz in repr_config.types_to_be_repr:
        return token.preprocessed_repr(repr_config)
    else:
        non_prep, metadata = token.non_preprocessed_repr(repr_config)
        return (non_prep if isinstance(non_prep, list) else [non_prep]), metadata
