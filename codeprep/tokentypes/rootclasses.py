# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
from abc import ABC, abstractmethod
from typing import List, Set, Optional

from codeprep.preprocess.codestructure import PureSnippetStructure
from codeprep.preprocess.reprconfig import ReprConfig
from codeprep.preprocess.result import PreprocessingResult
from codeprep.preprocess.tokens import TokenSequence
from codeprep.preprocess.metadata import PreppedTokenMetadata


class ParsedToken(ABC):
    def _wrap_in_metadata_for_full_word(self, tokens: List[str], n_additional_empty_line,
                                        non_proc: Optional[Set[str]] = None) -> PreprocessingResult:
        prepped_sub_token_sequence = TokenSequence.of(
            tokens,
            PreppedTokenMetadata(
                n_subtokens_per_token=[len(tokens)],
                token_types=[type(self)]
        ), word_end_token_added=False)
        non_processable_tokens = non_proc or {}
        return PreprocessingResult(prepped_sub_token_sequence, non_processable_tokens,
                                   PureSnippetStructure([len(tokens)] + [0] * n_additional_empty_line))

    @abstractmethod
    def preprocessed_repr(self, repr_config: ReprConfig) -> PreprocessingResult:
        pass

    @abstractmethod
    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> PreprocessingResult:
        pass


class ParsedSubtoken(ABC):
    @abstractmethod
    def preprocessed_repr(self, repr_config: ReprConfig) -> List[str]:
        pass

    @abstractmethod
    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> str:
        pass