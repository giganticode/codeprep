from typing import List, Set, Union

from dataclasses import dataclass, field

from codeprep.tokens import SurrogatePreppedTokenSequence, PreppedSubTokenSequence


@dataclass
class PreprocessingResult(object):
    prepped_tokens: Union[PreppedSubTokenSequence, SurrogatePreppedTokenSequence] = field(default_factory=PreppedSubTokenSequence)
    non_processable_tokens: Set[str] = field(default_factory=set)

    def update_(self, preprocessing_result: 'PreprocessingResult') -> 'PreprocessingResult':
        self.prepped_tokens = self.prepped_tokens.add(preprocessing_result.prepped_tokens)
        self.non_processable_tokens.update(preprocessing_result.non_processable_tokens)

        return self

    def get_single_token(self) -> str:
        if len(self.prepped_tokens) != 1:
            raise ValueError(f"This pre-processing result contains more than one token: {self.prepped_tokens}")

        return self.prepped_tokens.tokens[0]

    @staticmethod
    def with_empty_metadata(tokens: List[str]) -> 'PreprocessingResult':
        return PreprocessingResult(SurrogatePreppedTokenSequence(tokens))
