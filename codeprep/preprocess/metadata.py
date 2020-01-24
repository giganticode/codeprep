# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Set, Optional, List, Type, Tuple

from codeprep.subtokens import is_terminal_subtoken
from codeprep.util import to_literal_str

logger = logging.getLogger(__name__)


class InvalidMetadataError(Exception):
    pass


class PreprocessingMetadata(object):
    def __init__(self,
                 nonprocessable_tokens: Optional[Set[str]] = None,
                 word_boundaries: Optional[List[int]] = None,
                 token_types: List[Type] = None):
        self.nonprocessable_tokens = nonprocessable_tokens or set()
        self.word_boundaries = word_boundaries or [0]
        self.token_types = token_types or []

        self._check_invariants()

    def _check_invariants(self) -> None:
        assert len(self.word_boundaries) - 1 == len(self.token_types)

    def set_all_tokens_type(self, t: Type) -> None:
        self.token_types = [t] * (len(self.word_boundaries) -1)

    def update(self, preprocessing_metadata: 'PreprocessingMetadata') -> 'PreprocessingMetadata':
        """
        >>> class TypeA: pass
        >>> class TypeB: pass
        >>> PreprocessingMetadata().update(PreprocessingMetadata())
        (set(), [0], [])

        >>> PreprocessingMetadata({'<comment>'}, [0, 2], [TypeA]).update(PreprocessingMetadata({'<comment>'}, [0, 1, 2, 3], [TypeA, TypeA, TypeB]))
        ({'<comment>'}, [0, 2, 3, 4, 5], ['TypeA', 'TypeA', 'TypeA', 'TypeB'])

        >>> PreprocessingMetadata(set(), [0, 2], [TypeA]).update(PreprocessingMetadata(set(), [0, 3], [TypeB]))
        (set(), [0, 2, 5], ['TypeA', 'TypeB'])
        """
        self.nonprocessable_tokens.update(preprocessing_metadata.nonprocessable_tokens)

        n_subtokens = self.word_boundaries.pop()
        for boundary in preprocessing_metadata.word_boundaries:
            self.word_boundaries.append(n_subtokens + boundary)

        self.token_types.extend(preprocessing_metadata.token_types)

        return self

    def __repr__(self):
        return str((self.nonprocessable_tokens, self.word_boundaries, list(map(lambda x: x.__name__, self.token_types))))

    def __eq__(self, other):
        return self.__class__ == other.__class__ \
               and self.nonprocessable_tokens == other.nonprocessable_tokens \
               and self.word_boundaries == other.word_boundaries \
               and self.token_types == other.token_types


def save_metadata(metadata: PreprocessingMetadata, save_to: bytes) -> None:
    with open(save_to, 'w') as f:
        for token in metadata.nonprocessable_tokens:
            f.write(f'{to_literal_str(token)}\n')


def check_metadata_validity(subwords: List[str], metadata: PreprocessingMetadata, use_only_token_end_chars=True) -> None:
    word_boundaries = metadata.word_boundaries
    if len(word_boundaries) == 0:
        raise ValueError("Word boundaries list should contain at least 0!")
    if len(subwords) != word_boundaries[-1]:
        raise ValueError(f"Word boundaries list should contain the indices of the last word.\n"
                         f"However, the subword entropies list has {len(subwords)} elements, and "
                         f"value {len(subwords)} is not found in word boundaries list: {word_boundaries}")
    if word_boundaries[0] != 0:
        raise ValueError('Word boundaries list must start with 0!')

    if use_only_token_end_chars:
        for idx, token in enumerate(subwords):
            end_according_to_data = is_terminal_subtoken(token)
            end_according_to_metadata = (idx + 1) in metadata.word_boundaries
            if end_according_to_data != end_according_to_metadata:
                error_context_start_index = idx - 20 if idx - 20 > 0 else 0
                error_context_end_index = idx + 20 if idx + 20 < len(subwords) else len(subwords) - 1
                raise AssertionError(f'Token {token} according to metadata is'
                                     f'{" " if end_according_to_metadata else " NOT"} end-token. '
                                     f'Showing context: {subwords[error_context_start_index:error_context_end_index]}')


def with_empty_metadata(tokens: List[str]) -> Tuple[List[str], PreprocessingMetadata]:
    return tokens, PreprocessingMetadata()


def unwrap_single_string(tokens_and_metadata: Tuple[List[str], PreprocessingMetadata]) -> str:
    tokens = tokens_and_metadata[0]
    if isinstance(tokens, list) and len(tokens) == 1:
        return tokens[0]