# SPDX-FileCopyrightText: 2020 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Set

from dataclasses import dataclass, field

from codeprep.preprocess.codestructure import PureSnippetStructure
from codeprep.preprocess.tokens import TokenSequence


@dataclass
class PreprocessingResult(object):
    prepped_tokens: TokenSequence = field(default_factory=TokenSequence.empty)
    non_processable_tokens: Set[str] = field(default_factory=set)
    code_snippet_structure: PureSnippetStructure = PureSnippetStructure.empty()

    def __post_init__(self):
        if sum(self.prepped_tokens.metadata.n_subtokens_per_token) != len(self.code_snippet_structure):
            raise AssertionError()

    def update_(self, other: 'PreprocessingResult') -> 'PreprocessingResult':
        self.prepped_tokens.extend(other.prepped_tokens)
        self.non_processable_tokens.update(other.non_processable_tokens)
        self.code_snippet_structure = self.code_snippet_structure.merge(other.code_snippet_structure)

        return self

    def get_single_token(self) -> str:
        if len(self.prepped_tokens) != 1:
            raise ValueError(f"This pre-processing result contains more than one token: {self.prepped_tokens}")

        return self.prepped_tokens.tokens[0]
