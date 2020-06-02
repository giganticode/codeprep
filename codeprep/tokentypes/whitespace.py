# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
from abc import ABC
from typing import Optional

from codeprep.preprocess.codestructure import PureSnippetStructure
from codeprep.preprocess.core import ReprConfig
from codeprep.preprocess.result import PreprocessingResult
from codeprep.preprocess.placeholders import placeholders
from codeprep.tokentypes.rootclasses import ParsedToken

NBSP = '\xa0'


class Whitespace(ParsedToken, ABC):
    def __eq__(self, other):
        return other.__class__ == self.__class__

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

    def __str__(self):
        return self.non_preprocessed_repr().get_single_token()


class NewLine(Whitespace):
    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> PreprocessingResult:
        return self._wrap_in_metadata_for_full_word(["\n"], 1, non_proc={"\n"})

    def preprocessed_repr(self, repr_config: ReprConfig) -> PreprocessingResult:
        return PreprocessingResult(code_snippet_structure=PureSnippetStructure.empty_line())


class Tab(Whitespace):
    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> PreprocessingResult:
        return self._wrap_in_metadata_for_full_word(["\t"], 0, non_proc={"\t"})

    def preprocessed_repr(self, repr_config: ReprConfig) -> PreprocessingResult:
        return PreprocessingResult()


class SpaceInString(Whitespace):
    def __init__(self, n_chars: int = 1):
        super().__init__()
        self.n_chars = n_chars

    def preprocessed_repr(self, repr_config: ReprConfig) -> PreprocessingResult:
        raise NotImplemented()

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> PreprocessingResult:
        return self._wrap_in_metadata_for_full_word([placeholders['space_in_str'] * self.n_chars], 0)

    def __repr__(self):
        return f'<{self.__class__.__name__}> (n_chars={self.n_chars})'

    def __eq__(self, other):
        return other.__class__ == self.__class__ and other.n_chars == self.n_chars