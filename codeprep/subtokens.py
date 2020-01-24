# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import List, Callable, Any

from codeprep.preprocess.placeholders import placeholders


class TokenIterator(object):
    def __init__(self, subwords, word_boundaries, format, return_full_token_index):
        self.validate_word_boundaries(subwords, word_boundaries)

        self.subwords = subwords
        self.word_boundaries = word_boundaries
        self.format = format
        self.return_full_token_index = return_full_token_index

    def __iter__(self):
        return self

    @staticmethod
    def validate_word_boundaries(subwords: List[str], word_boundaries: List[int]) -> None:
        if len(word_boundaries) == 0:
            raise ValueError("Word boundaries list should contain at least 0!")
        if len(subwords) != word_boundaries[-1]:
            raise ValueError(f"Word boundaries list should contain the indices of the last word.\n"
                             f"However, the subword entropies list has {len(subwords)} elements, and "
                             f"value {len(subwords)} is not found in word boundaries list: {word_boundaries}")
        if word_boundaries[0] != 0:
            raise ValueError('Word boundaries list must start with 0!')


class SubtokenIterator(TokenIterator):
    """
    >>> [token for token in SubtokenIterator(['hi', 'the', 're'], [0, 1, 3])]
    ['hi', 'the', 're']

    >>> [token for token in SubtokenIterator([1, 2, 3], [0, 1, 3], format=lambda s: str(s[0]))]
    ['1', '2', '3']

    >>> [token for token in SubtokenIterator(['hi', 'the', 're'], [0, 1, 3], return_full_token_index=True)]
    [(0, 'hi'), (1, 'the'), (1, 're')]

    >>> [token for token in SubtokenIterator(['hi'], [0])]
    Traceback (most recent call last):
    ...
    ValueError: Word boundaries list should contain the indices of the last word.
    However, the subword entropies list has 1 elements, and value 1 is not found in word boundaries list: [0]

    >>> [token for token in SubtokenIterator(['hi'], [1])]
    Traceback (most recent call last):
    ...
    ValueError: Word boundaries list must start with 0!
    """
    def __init__(self, subwords: List[Any],
                 word_boundaries: List[int],
                 format: Callable[[List[str]], Any] = lambda l: l[0],
                 return_full_token_index: bool = False):

        super().__init__(subwords, word_boundaries, format, return_full_token_index)

        self.current_index = 0
        self.current_full_word = 0

    def __next__(self):
        if self.current_index >= len(self.subwords):
            raise StopIteration

        value = [self.subwords[self.current_index]]
        formatted_value = self.format(value)
        result = (self.current_full_word, formatted_value) if self.return_full_token_index else formatted_value

        self.current_index += 1
        if self.word_boundaries[self.current_full_word + 1] == self.current_index:
            self.current_full_word += 1

        return result


class FullTokenIterator(TokenIterator):
    """
    >>> [token for token in FullTokenIterator(['hi', 'the', 're'], [0, 1, 3])]
    ['hi', 'there']

    >>> [token for token in FullTokenIterator(['hel', 'l', 'o'], [0, 3])]
    ['hello']

    >>> [token for token in FullTokenIterator([1, 2, 4], [0, 2, 3], format=sum)]
    [3, 4]

    >>> [token for token in FullTokenIterator(['hi', 'the', 're'], [0, 1, 3], return_full_token_index=True)]
    [(0, 'hi'), (1, 'there')]

    >>> [token for token in FullTokenIterator([], [])]
    Traceback (most recent call last):
    ...
    ValueError: Word boundaries list should contain at least 0!

    >>> [token for token in FullTokenIterator(['hi'], [0])]
    Traceback (most recent call last):
    ...
    ValueError: Word boundaries list should contain the indices of the last word.
    However, the subword entropies list has 1 elements, and value 1 is not found in word boundaries list: [0]

    >>> [token for token in FullTokenIterator(['hi'], [1])]
    Traceback (most recent call last):
    ...
    ValueError: Word boundaries list must start with 0!
    """
    def __init__(self, subwords: List[Any],
                 word_boundaries: List[int],
                 format: Callable[[List[str]], Any] = lambda s: ''.join(s),
                 return_full_token_index: bool = False):
        super().__init__(subwords, word_boundaries, format, return_full_token_index)

        self.current_full_word = 0

    def __next__(self):
        if self.current_full_word >= len(self.word_boundaries) - 1:
            raise StopIteration

        word_start = self.word_boundaries[self.current_full_word]
        word_end = self.word_boundaries[self.current_full_word + 1]
        formatted_value = self.format(self.subwords[word_start:word_end])
        result = (self.current_full_word, formatted_value) if self.return_full_token_index else formatted_value

        self.current_full_word += 1

        return result


def is_terminal_subtoken(subtoken: str, use_token_end_chars: bool = True) -> bool:
    if not use_token_end_chars:
        raise NotImplemented("Finding out if a subtoken is terminal for tokens represented with <w> and </w> tokens "
                             "is not yet implemented.")

    return subtoken.endswith(placeholders['compound_word_end'])