# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import List, Tuple, Optional

from codeprep.noneng import replace_non_ascii_seqs
from codeprep.preprocess.core import ReprConfig, torepr
from codeprep.preprocess.metadata import PreprocessingMetadata
from codeprep.preprocess.placeholders import placeholders
from codeprep.tokens.containers import SplitContainer
from codeprep.tokens.rootclasses import ParsedToken


class NonEng(ParsedToken):
    def __init__(self, processable_token: SplitContainer):
        if not isinstance(processable_token, SplitContainer):
            raise ValueError(f"Only SplitContainer can be wrapped in {self.__class__}. Type passed: {type(processable_token)}")

        self.processable_token = processable_token

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
        return torepr(self.processable_token, repr_config)

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        if repr_config.bpe_data:
            token = replace_non_ascii_seqs(str(self.processable_token), placeholders['non_ascii_seq'])
            return torepr(SplitContainer.from_single_token(token), repr_config)
        else:
            return self.wrap_in_metadata_for_full_word([placeholders['non_eng']])

    def __repr__(self):
        return f'{self.__class__.__name__}({self.processable_token.__repr__()})'

    def __str__(self):
        return str(self.processable_token)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.processable_token == other.processable_token