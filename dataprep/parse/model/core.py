from typing import List, Tuple, Union

from dataprep.parse.model.metadata import PreprocessingMetadata


def with_empty_metadata(tokens: Union[List[str], str]) -> Tuple[Union[List[str], str], PreprocessingMetadata]:
    return tokens, PreprocessingMetadata()


class ParsedToken(object):
    def with_full_word_metadata(self, tokens: Union[List[str], str], metadata: PreprocessingMetadata=None) -> Tuple[Union[List[str], str], PreprocessingMetadata]:
        updated_metadata = metadata or PreprocessingMetadata()
        updated_metadata.word_boundaries = [0, len(tokens) if isinstance(tokens, list) else 1]
        return tokens, updated_metadata


class ParsedSubtoken(object):
    pass
