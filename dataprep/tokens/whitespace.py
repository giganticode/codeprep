from typing import List, Tuple, Optional

from dataprep.preprocess.core import ReprConfig
from dataprep.preprocess.metadata import PreprocessingMetadata, unwrap_single_string
from dataprep.preprocess.placeholders import placeholders
from dataprep.tokens.rootclasses import ParsedToken

NBSP = '\xa0'


class Whitespace(ParsedToken):
    def __eq__(self, other):
        return other.__class__ == self.__class__

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

    def __str__(self):
        return unwrap_single_string(self.non_preprocessed_repr())


class NewLine(Whitespace):
    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
        return self.wrap_in_metadata_for_full_word(["\n"], non_proc={"\n"})

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return [], PreprocessingMetadata()


class Tab(Whitespace):
    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
        return self.wrap_in_metadata_for_full_word(["\t"], non_proc={"\t"})

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return [], PreprocessingMetadata()


class SpaceInString(Whitespace):

    def __init__(self, n_chars: int = 1):
        super().__init__()
        self.n_chars = n_chars

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
        return self.wrap_in_metadata_for_full_word([placeholders['space_in_str'] * self.n_chars])

    def __repr__(self):
        return f'<{self.__class__.__name__}> (n_chars={self.n_chars})'

    def __eq__(self, other):
        return other.__class__ == self.__class__ and other.n_chars == self.n_chars
