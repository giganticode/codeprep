from typing import Generator, Union, Tuple, List

from dataprep.model.core import ParsedToken
from dataprep.model.metadata import PreprocessingMetadata
from dataprep.split.ngram import NgramSplitConfig


class ReprConfig(object):
    def __init__(self, types_to_be_repr, ngram_split_config, dict_based_non_eng=True, should_lowercase=True):
        self.types_to_be_repr = types_to_be_repr
        self.ngram_split_config = ngram_split_config
        self.dict_based_non_eng = dict_based_non_eng
        self.should_lowercase = should_lowercase

    @classmethod
    def empty(cls):
        return cls([], NgramSplitConfig())


def to_repr_list(token_list: Generator[Union[str, ParsedToken], None, None], repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
    repr_res = []
    all_metadata = PreprocessingMetadata()
    for token in token_list:
        repr_token, metadata = torepr(token, repr_config)
        repr_res.extend(repr_token)
        all_metadata.update(metadata)
    return repr_res, all_metadata


def torepr(token, repr_config) -> Tuple[List[str], PreprocessingMetadata]:
    clazz = type(token)
    if clazz.__name__ == 'ParseableToken':
        raise AssertionError(f"Parseable token cannot be present in the final parsed model: {token}")
    if clazz == list:
        return to_repr_list(token, repr_config)
    if clazz == str:
        return [token], PreprocessingMetadata(nonprocessable_tokens={token}, word_boundaries=[0,1])

    if clazz in repr_config.types_to_be_repr:
        return token.preprocessed_repr(repr_config)
    else:
        non_prep, metadata = token.non_preprocessed_repr(repr_config)
        return (non_prep if isinstance(non_prep, list) else [non_prep]), metadata