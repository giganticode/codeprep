# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import List, Tuple, Set, Optional

from codeprep.preprocess.metadata import PreprocessingMetadata


class ParsedToken(object):
    def wrap_in_metadata_for_full_word(self, tokens: List[str], non_proc: Optional[Set[str]] = None) \
            -> Tuple[List[str], PreprocessingMetadata]:
        assert type(tokens) == list

        metadata = PreprocessingMetadata()
        metadata.nonprocessable_tokens = non_proc or []
        metadata.word_boundaries = [0, len(tokens)]
        metadata.token_types = [type(self)]
        return tokens, metadata


class ParsedSubtoken(object):
    pass