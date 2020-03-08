# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import List, Set, Optional

from codeprep.preprocess.result import PreprocessingResult
from codeprep.tokens import PreppedTokenSequence, PreppedSubTokenSequence
from codeprep.preprocess.metadata import PreppedTokenMetadata


class ParsedToken(object):
    def _wrap_in_metadata_for_full_word(self, tokens: List[str], non_proc: Optional[Set[str]] = None) -> PreprocessingResult:
        prepped_sub_token_sequence = PreppedSubTokenSequence(
            tokens,
            PreppedTokenMetadata(
                n_subtokens_per_token=[len(tokens)],
                token_types=[type(self)]
        ))
        non_processable_tokens = non_proc or []
        return PreprocessingResult(prepped_sub_token_sequence, non_processable_tokens)


class ParsedSubtoken(object):
    pass