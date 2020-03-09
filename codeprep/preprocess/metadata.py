# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import List, Type

from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PreppedTokenMetadata(object):
    n_subtokens_per_token: List[int] = field(default_factory=list)
    token_types: List[Type] = field(default_factory=list)

    def __post__init__(self) -> None:
        assert len(self.n_subtokens_per_token) == len(self.token_types)

    def set_all_tokens_type(self, t: Type) -> None:
        self.token_types = [t] * len(self.n_subtokens_per_token)

    def update_(self, preprocessing_metadata: 'PreppedTokenMetadata') -> 'PreppedTokenMetadata':
        """
        >>> class TypeA: pass
        >>> class TypeB: pass
        >>> PreppedTokenMetadata().update_(PreppedTokenMetadata())
        ([], [])

        >>> PreppedTokenMetadata([2], [TypeA]).update_(PreppedTokenMetadata([1, 2, 3], [TypeA, TypeA, TypeB]))
        ([2, 1, 2, 3], ['TypeA', 'TypeA', 'TypeA', 'TypeB'])

        >>> metadata = PreppedTokenMetadata([2], [TypeA]).update_(PreppedTokenMetadata([3], [TypeB]))
        >>> metadata
        ([2, 3], ['TypeA', 'TypeB'])
        """

        self.n_subtokens_per_token.extend(preprocessing_metadata.n_subtokens_per_token)
        self.token_types.extend(preprocessing_metadata.token_types)

        return self

    def __repr__(self):
        return str((self.n_subtokens_per_token, list(map(lambda x: x.__name__, self.token_types))))

    def __len__(self):
        return len(self.n_subtokens_per_token)

    def token_type(self) -> Type:
        if len(self.token_types) != 1:
            raise ValueError("This method can be only called if the sequence contains only one token.")

        return self.token_types[0]

    def n_subtokens(self) -> int:
        if len(self.n_subtokens_per_token) != 1:
            raise ValueError("This method can be only called if the sequence contains only one token.")

        return self.n_subtokens_per_token[0]


