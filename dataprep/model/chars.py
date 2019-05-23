from typing import List, Tuple

from dataprep.model.core import ParsedToken
from dataprep.model.metadata import PreprocessingMetadata
from dataprep.preprocessors.repr import ReprConfig


class SpecialChar(ParsedToken):
    def __eq__(self, other):
        return other.__class__ == self.__class__

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

    def __str__(self):
        return self.non_preprocessed_repr(ReprConfig.empty())[0]


class NewLine(SpecialChar):
    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[str, PreprocessingMetadata]:
        return "\n", PreprocessingMetadata({"\n"})

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return [], PreprocessingMetadata()


class Tab(SpecialChar):
    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[str, PreprocessingMetadata]:
        return "\t", PreprocessingMetadata({"\t"})

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return [], PreprocessingMetadata()


class Backslash(SpecialChar):
    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[str, PreprocessingMetadata]:
        return "\\", PreprocessingMetadata({"\\"})


class Quote(SpecialChar):
    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[str, PreprocessingMetadata]:
        return "\"", PreprocessingMetadata({"\""})


class MultilineCommentStart(SpecialChar):
    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[str, PreprocessingMetadata]:
        return "/*", PreprocessingMetadata({"/*"})


class MultilineCommentEnd(SpecialChar):
    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[str, PreprocessingMetadata]:
        return "*/", PreprocessingMetadata({"*/"})


class OneLineCommentStart(SpecialChar):
    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[str, PreprocessingMetadata]:
        return "//", PreprocessingMetadata({"//"})
