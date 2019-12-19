from typing import List, Tuple, Set, Optional

from dataprep.parse.model.metadata import PreprocessingMetadata


def with_empty_metadata(tokens: List[str]) -> Tuple[List[str], PreprocessingMetadata]:
    return tokens, PreprocessingMetadata()


def unwrap_single_string(tokens_and_metadata: Tuple[List[str], PreprocessingMetadata]) -> str:
    tokens = tokens_and_metadata[0]
    if isinstance(tokens, list) and len(tokens) == 1:
        return tokens[0]


class ParsedToken(object):
    def wrap_in_metadata_for_full_word(self, tokens: List[str], non_proc: Optional[Set[str]] = None) \
            -> Tuple[List[str], PreprocessingMetadata]:
        assert type(tokens) == list

        metadata = PreprocessingMetadata()
        metadata.nonprocessable_tokens = non_proc or []
        metadata.word_boundaries = [0, len(tokens)]
        metadata.token_types = [type(self)]
        return tokens, metadata


class ParsedSubtoken(object):
    pass
