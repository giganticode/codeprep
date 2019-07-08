from typing import List, Tuple

from dataprep.parse.model.core import ParsedToken
from dataprep.parse.model.metadata import PreprocessingMetadata
from dataprep.parse.model.placeholders import placeholders
from dataprep.preprocess.core import ReprConfig


class Number(ParsedToken):
    def __init__(self, parts_of_number):
        if not isinstance(parts_of_number, list):
            raise ValueError(f"Parts of number must be list but is {type(parts_of_number)}")
        self.parts_of_number = parts_of_number

    def __str__(self):
        return self.non_preprocessed_repr(ReprConfig.empty())[0]

    def __repr__(self):
        return f'{self.__class__.__name__}{self.parts_of_number}'

    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[str, PreprocessingMetadata]:
        return self.with_full_word_metadata("".join([str(w) for w in self.parts_of_number]))

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        subwords = repr_config.number_splitter(self.non_preprocessed_repr(repr_config)[0], repr_config.bpe_data)

        if len(subwords ) > 1:
            subwords_with_boundaries = [placeholders['word_start']] + subwords + [placeholders['word_end']]
            return self.with_full_word_metadata(subwords_with_boundaries)
        else:
            return self.with_full_word_metadata(subwords)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.parts_of_number == other.parts_of_number
