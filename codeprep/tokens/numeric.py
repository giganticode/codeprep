# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import List, Tuple, Optional

from codeprep.preprocess.core import ReprConfig
from codeprep.preprocess.metadata import PreprocessingMetadata, unwrap_single_string
from codeprep.preprocess.placeholders import placeholders
from codeprep.tokens.rootclasses import ParsedToken


class Number(ParsedToken):
    def __init__(self, val: str):
        self.val = val.lower()

    def __str__(self):
        return unwrap_single_string(self.non_preprocessed_repr())

    def __repr__(self):
        return f'<{self.__class__.__name__}>({self.val})'

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
        return self.wrap_in_metadata_for_full_word([self.val])

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        subwords = repr_config.number_splitter(self.non_preprocessed_repr()[0][0], repr_config.bpe_data)

        if len(subwords) > 1 and not repr_config.bpe_data:
            prep_number = [placeholders['word_start']] + subwords + [placeholders['word_end']]
        else:
            prep_number = subwords

        return self.wrap_in_metadata_for_full_word(prep_number)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.val == other.val


class One(Number):
    def __init__(self):
        super().__init__('1')


class Zero(Number):
    def __init__(self):
        super().__init__('0')