from typing import List, Set

from dataclasses import dataclass, field

from codeprep.preprocess.metadata import PreprocessingMetadata


@dataclass
class PreprocessingResult(object):
    tokens: List[str] = field(default_factory=list)
    metadata: PreprocessingMetadata = field(default_factory=PreprocessingMetadata)
    non_processable_tokens: Set[str] = field(default_factory=set)

    def __post_init__(self):
        assert isinstance(self.tokens, list)

    def update_(self, preprocessing_result: 'PreprocessingResult') -> 'PreprocessingResult':
        self.tokens.extend(preprocessing_result.tokens)
        self.metadata.update(preprocessing_result.metadata)
        self.non_processable_tokens.update(preprocessing_result.non_processable_tokens)

        return self


def with_empty_metadata(tokens: List[str]) -> PreprocessingResult:
    return PreprocessingResult(tokens)


def unwrap_single_string(preprocessing_result: PreprocessingResult) -> str:
    tokens = preprocessing_result.tokens
    if isinstance(tokens, list) and len(tokens) == 1:
        return tokens[0]