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


class ParseableToken(object):
    """
    This class represents parts of input that still needs to be parsed
    """

    def __init__(self, val: str):
        if not isinstance(val, str):
            raise ValueError(f"val should be str but is {type(val)}")
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return f'{self.__class__.__name__}({self.val})'

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.val == other.val
