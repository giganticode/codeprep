# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import List, Callable, Any

from codeprep.preprocess.metadata import PreppedTokenMetadata, check_metadata_validity
from codeprep.tokens.containers import SplitContainer


class TokenIterator(object):
    def __init__(self, subwords: List[Any], metadata: PreppedTokenMetadata,
                 format: Callable[[List[Any]], Any], return_full_token_index: bool):
        check_metadata_validity(subwords, metadata, use_only_token_end_chars=False)

        self.subwords = subwords
        self.metadata = metadata
        self.format = format
        self.return_full_token_index = return_full_token_index

    def __iter__(self):
        return self


class SubtokenIterator(TokenIterator):
    """
    >>> [token for token in SubtokenIterator(['hi', 'the', 're'], PreppedTokenMetadata([1, 2], [SplitContainer, SplitContainer]))]
    ['hi', 'the', 're']

    >>> [token for token in SubtokenIterator([1, 2, 3], PreppedTokenMetadata([1, 2], [SplitContainer, SplitContainer]), format=lambda s: str(s[0]))]
    ['1', '2', '3']

    >>> [token for token in SubtokenIterator(['hi', 'the', 're'], PreppedTokenMetadata([1, 2], [SplitContainer, SplitContainer]), return_full_token_index=True)]
    [(0, 'hi'), (1, 'the'), (1, 're')]

    >>> [token for token in SubtokenIterator(['hi'], PreppedTokenMetadata([1, 2], [SplitContainer, SplitContainer]))]
    Traceback (most recent call last):
    ...
    ValueError: Tokens and metadata are out-of-sync.
    The subword entropy list has 1 elements but the number of sub-tokens according to metadata is 3.

    """
    def __init__(self, subwords: List[Any],
                 metadata: PreppedTokenMetadata,
                 format: Callable[[List[str]], Any] = lambda l: l[0],
                 return_full_token_index: bool = False):

        super().__init__(subwords, metadata, format, return_full_token_index)

        self.current_index = 0
        self.current_subword_in_word = 0
        self.current_full_word = 0

    def __next__(self):
        if self.current_index >= len(self.subwords):
            raise StopIteration

        value = [self.subwords[self.current_index]]
        formatted_value = self.format(value)
        result = (self.current_full_word, formatted_value) if self.return_full_token_index else formatted_value

        self.current_index += 1
        self.current_subword_in_word += 1
        if self.metadata.n_subtokens_per_token[self.current_full_word] == self.current_subword_in_word:
            self.current_full_word += 1
            self.current_subword_in_word = 0

        return result


class FullTokenIterator(TokenIterator):
    """
    >>> [token for token in FullTokenIterator(['hi', 'the', 're'], PreppedTokenMetadata([1, 2], [SplitContainer, SplitContainer]))]
    ['hi', 'there']

    >>> [token for token in FullTokenIterator(['hel', 'l', 'o'], PreppedTokenMetadata([3], [SplitContainer]))]
    ['hello']

    >>> [token for token in FullTokenIterator([1, 2, 4], PreppedTokenMetadata([2, 1], [SplitContainer, SplitContainer]), format=sum)]
    [3, 4]

    >>> [token for token in FullTokenIterator(['hi', 'the', 're'], PreppedTokenMetadata([1, 2], [SplitContainer, SplitContainer]), return_full_token_index=True)]
    [(0, 'hi'), (1, 'there')]
    """
    def __init__(self, subwords: List[Any],
                 metadata: PreppedTokenMetadata,
                 format: Callable[[List[str]], Any] = lambda s: ''.join(s),
                 return_full_token_index: bool = False):
        super().__init__(subwords, metadata, format, return_full_token_index)

        self.current_full_word = 0
        self.current_index = 0

    def __next__(self):
        if self.current_full_word >= len(self.metadata.n_subtokens_per_token):
            raise StopIteration

        sub_words_in_current_full_word = self.metadata.n_subtokens_per_token[self.current_full_word]
        formatted_value = self.format(self.subwords[self.current_index:self.current_index+sub_words_in_current_full_word])
        result = (self.current_full_word, formatted_value) if self.return_full_token_index else formatted_value

        self.current_full_word += 1
        self.current_index += sub_words_in_current_full_word

        return result
