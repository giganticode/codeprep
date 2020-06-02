# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Optional

from codeprep.noneng import replace_non_ascii_seqs
from codeprep.preprocess.core import ReprConfig, torepr
from codeprep.preprocess.result import PreprocessingResult
from codeprep.preprocess.placeholders import placeholders
from codeprep.tokentypes.containers import Identifier
from codeprep.tokentypes.rootclasses import ParsedToken


class NonEng(ParsedToken):
    def __init__(self, processable_token: Identifier):
        if not isinstance(processable_token, Identifier):
            raise ValueError(f"Only Identifier can be wrapped in {self.__class__}. Type passed: {type(processable_token)}")

        self.processable_token = processable_token

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> PreprocessingResult:
        return torepr(self.processable_token, repr_config)

    def preprocessed_repr(self, repr_config: ReprConfig) -> PreprocessingResult:
        if repr_config.bpe_data:
            token = replace_non_ascii_seqs(str(self.processable_token), placeholders['non_ascii_seq'])
            return torepr(Identifier.from_single_token(token), repr_config)
        else:
            return self._wrap_in_metadata_for_full_word([placeholders['non_eng']], 0)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.processable_token.__repr__()})'

    def __str__(self):
        return str(self.processable_token)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.processable_token == other.processable_token