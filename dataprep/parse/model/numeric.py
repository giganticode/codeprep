from typing import List, Tuple, Optional

from dataprep.parse.model.core import ParsedToken
from dataprep.parse.model.metadata import PreprocessingMetadata
from dataprep.parse.model.placeholders import placeholders
from dataprep.preprocess.core import ReprConfig


class Number(ParsedToken):
    def __init__(self, val: str):
        self.val = val.lower()

    def __str__(self):
        return self.non_preprocessed_repr()[0]

    def __repr__(self):
        return f'{self.__class__.__name__}{self.val}'

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[str, PreprocessingMetadata]:
        return self.with_full_word_metadata(self.val)

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        subwords = repr_config.number_splitter(self.non_preprocessed_repr()[0], repr_config.bpe_data)

        if len(subwords) > 1 and not repr_config.bpe_data:
            prep_number = [placeholders['word_start']] + subwords + [placeholders['word_end']]
        else:
            prep_number = subwords

        return self.with_full_word_metadata(prep_number)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.val == other.val
