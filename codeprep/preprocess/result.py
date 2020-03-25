from typing import Set

from dataclasses import dataclass, field

from codeprep.preprocess.tokens import TokenSequence


@dataclass
class PreprocessingResult(object):
    prepped_tokens: TokenSequence = field(default_factory=TokenSequence.empty)
    non_processable_tokens: Set[str] = field(default_factory=set)

    def update_(self, preprocessing_result: 'PreprocessingResult') -> 'PreprocessingResult':
        self.prepped_tokens = self.prepped_tokens.add(preprocessing_result.prepped_tokens)
        self.non_processable_tokens.update(preprocessing_result.non_processable_tokens)

        return self

    def get_single_token(self) -> str:
        if len(self.prepped_tokens) != 1:
            raise ValueError(f"This pre-processing result contains more than one token: {self.prepped_tokens}")

        return self.prepped_tokens.tokens[0]
