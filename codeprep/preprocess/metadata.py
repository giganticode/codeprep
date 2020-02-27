# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Set, Optional, List, Type

from codeprep.subtokens import is_terminal_subtoken
from codeprep.util import to_literal_str

logger = logging.getLogger(__name__)


class InvalidMetadataError(Exception):
    pass


class PreppedTokenMetadata(object):
    def __init__(self,
                 n_subtokens_per_token: Optional[List[int]] = None,
                 token_types: List[Type] = None):
        self.n_subtokens_per_token = n_subtokens_per_token or []
        self.token_types = token_types or []

        self._check_invariants()

    def _check_invariants(self) -> None:
        assert len(self.n_subtokens_per_token) == len(self.token_types)

    def set_all_tokens_type(self, t: Type) -> None:
        self.token_types = [t] * len(self.n_subtokens_per_token)

    def update(self, preprocessing_metadata: 'PreppedTokenMetadata') -> 'PreppedTokenMetadata':
        """
        >>> class TypeA: pass
        >>> class TypeB: pass
        >>> PreppedTokenMetadata().update(PreppedTokenMetadata())
        ([], [])

        >>> PreppedTokenMetadata([2], [TypeA]).update(PreppedTokenMetadata([1, 2, 3], [TypeA, TypeA, TypeB]))
        ([2, 1, 2, 3], ['TypeA', 'TypeA', 'TypeA', 'TypeB'])

        >>> PreppedTokenMetadata([2], [TypeA]).update(PreppedTokenMetadata([3], [TypeB]))
        ([2, 3], ['TypeA', 'TypeB'])
        """

        self.n_subtokens_per_token.extend(preprocessing_metadata.n_subtokens_per_token)
        self.token_types.extend(preprocessing_metadata.token_types)

        return self

    def __repr__(self):
        return str((self.n_subtokens_per_token, list(map(lambda x: x.__name__, self.token_types))))

    def __eq__(self, other):
        return self.__class__ == other.__class__ \
               and self.n_subtokens_per_token == other.n_subtokens_per_token \
               and self.token_types == other.token_types


def save_non_processable_tokens(non_processable_tokens: Set[str], save_to: bytes) -> None:
    with open(save_to, 'w') as f:
        for token in non_processable_tokens:
            f.write(f'{to_literal_str(token)}\n')


def check_metadata_validity(subwords: List[str], metadata: PreppedTokenMetadata, use_only_token_end_chars=True) -> None:
    """
    >>> check_metadata_validity(['h', 'i</t>'], PreppedTokenMetadata([1], [object]))
    Traceback (most recent call last):
    ...
    ValueError: Tokens and metadata are out-of-sync.
    The subword entropy list has 2 elements but the number of sub-tokens according to metadata is 1.

    >>> check_metadata_validity(['h</t>', 'i</t>'], PreppedTokenMetadata([2], [object]))
    Traceback (most recent call last):
    ...
    AssertionError: Token h</t> according to metadata is NOT end-token. Showing context: ['h</t>']

    >>> check_metadata_validity(['h', 'i</t>', 'the', 'r', 'e</t>'], PreppedTokenMetadata([2, 1, 2], [object, object, object]))
    Traceback (most recent call last):
    ...
    AssertionError: Token the according to metadata is end-token. Showing context: ['h', 'i</t>', 'the', 'r']
    """
    n_subtokens_per_token = metadata.n_subtokens_per_token
    if len(subwords) != sum(n_subtokens_per_token):
        raise ValueError(f"Tokens and metadata are out-of-sync.\n"
                         f"The subword entropy list has {len(subwords)} elements but "
                         f"the number of sub-tokens according to metadata is {sum(n_subtokens_per_token)}.")

    if use_only_token_end_chars:
        current_token = 0
        current_subtoken = 0
        for idx, sub_token in enumerate(subwords):
            end_according_to_data = is_terminal_subtoken(sub_token)

            current_subtoken += 1
            end_according_to_metadata = (n_subtokens_per_token[current_token] == current_subtoken)
            if end_according_to_metadata:
                current_subtoken = 0
                current_token += 1
            if end_according_to_data != end_according_to_metadata:
                error_context_start_index = idx - 20 if idx - 20 > 0 else 0
                error_context_end_index = idx + 20 if idx + 20 < len(subwords) else len(subwords) - 1
                raise AssertionError(f'Token {sub_token} according to metadata is'
                                     f'{"" if end_according_to_metadata else " NOT"} end-token. '
                                     f'Showing context: {subwords[error_context_start_index:error_context_end_index]}')
