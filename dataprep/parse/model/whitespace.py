from typing import List, Tuple

from dataprep.parse.model.core import ParsedToken
from dataprep.parse.model.metadata import PreprocessingMetadata
from dataprep.preprocess.core import ReprConfig


class Whitespace(ParsedToken):
    def __eq__(self, other):
        return other.__class__ == self.__class__

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

    def __str__(self):
        return self.non_preprocessed_repr(ReprConfig.empty())[0]


class NewLine(Whitespace):
    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[str, PreprocessingMetadata]:
        return "\n", PreprocessingMetadata(nonprocessable_tokens={"\n"}, word_boundaries=[0,1])

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return [], PreprocessingMetadata()


class Tab(Whitespace):
    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[str, PreprocessingMetadata]:
        return "\t", PreprocessingMetadata({"\t"}, word_boundaries=[0,1])

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return [], PreprocessingMetadata()
