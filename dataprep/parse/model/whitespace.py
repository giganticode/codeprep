from typing import List, Tuple, Optional

from dataprep.parse.model.core import ParsedToken
from dataprep.parse.model.metadata import PreprocessingMetadata
from dataprep.preprocess.core import ReprConfig

NBSP = '\xa0'


class Whitespace(ParsedToken):
    def __eq__(self, other):
        return other.__class__ == self.__class__

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

    def __str__(self):
        return self.non_preprocessed_repr()[0]


class NewLine(Whitespace):
    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[str, PreprocessingMetadata]:
        return "\n", PreprocessingMetadata(nonprocessable_tokens={"\n"}, word_boundaries=[0,1])

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return [], PreprocessingMetadata()


class Tab(Whitespace):
    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[str, PreprocessingMetadata]:
        return "\t", PreprocessingMetadata({"\t"}, word_boundaries=[0,1])

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return [], PreprocessingMetadata()


class SpaceInString(Whitespace):

    def __init__(self, n_chars: int = 1):
        super().__init__()
        self.n_chars = n_chars

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[str, PreprocessingMetadata]:
        return NBSP * self.n_chars, PreprocessingMetadata(word_boundaries=[0,1])

    def __repr__(self):
        return f'<{self.__class__.__name__}> (n_chars={self.n_chars})'

    def __eq__(self, other):
        return other.__class__ == self.__class__ and other.n_chars == self.n_chars
