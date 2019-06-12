from typing import List, Tuple

from dataprep.model.core import ParsedToken
from dataprep.model.metadata import PreprocessingMetadata
from dataprep.model.placeholders import placeholders
from dataprep.preprocess.core import ReprConfig
from dataprep.split.ngram import NgramSplittingType, do_ngram_splitting


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
        return "".join([str(w) for w in self.parts_of_number]), PreprocessingMetadata()

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str],PreprocessingMetadata]:
        if repr_config.ngram_split_config is None:
            r, metadata = self.non_preprocessed_repr(repr_config)
            return (r if isinstance(r, list) else [r]), metadata

        if repr_config.ngram_split_config.splitting_type == NgramSplittingType.ONLY_NUMBERS:
            subwords = [str(w) for w in self.parts_of_number]
        elif repr_config.ngram_split_config.splitting_type is not None:
            subwords = do_ngram_splitting(self.non_preprocessed_repr(repr_config)[0], repr_config.ngram_split_config)
        else:
            subwords = [self.non_preprocessed_repr(repr_config)[0]]

        if len(subwords ) > 1:
            return [placeholders['word_start']] + subwords + [placeholders['word_end']], PreprocessingMetadata()
        else:
            return subwords, PreprocessingMetadata()

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.parts_of_number == other.parts_of_number
