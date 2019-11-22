from typing import List, Callable, Any

from dataprep.parse.model.placeholders import placeholders


class SubtokenIterator(object):
    def __init__(self, subwords: List[Any], word_boundaries: List[int], agg: Callable[[List[str]], Any]):
        self.it = iter(subwords)

    def __iter__(self):
        return self

    def __next__(self):
        return [next(self.it)], 1


class FullTokenIterator(object):
    """
    >>> [token for token in FullTokenIterator(['hi', 'the', 're'], [0, 1, 3])]
    ['hi', 'there']

    >>> [token for token in FullTokenIterator(['hel', 'l', 'o'], [0, 3])]
    ['hello']

    >>> [token for token in FullTokenIterator([1, 2, 4], [0, 2, 3], agg=sum)]
    [3, 4]

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
                 agg: Callable[[List[str]], Any] = lambda s: ''.join(s)):
        if len(word_boundaries) == 0:
            raise ValueError("Word boundaries list should contain at least 0!")
        if len(subwords) != word_boundaries[-1]:
            raise ValueError(f"Word boundaries list should contain the indices of the last word.\n"
                             f"However, the subword entropies list has {len(subwords)} elements, and "
                             f"value {len(subwords)} is not found in word boundaries list: {word_boundaries}")
        if word_boundaries[0] != 0:
            raise ValueError('Word boundaries list must start with 0!')

        self.subwords = subwords
        self.word_boundaries = word_boundaries
        self.agg = agg
        self.current_full_word = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_full_word >= len(self.word_boundaries) - 1:
            raise StopIteration
        word_start = self.word_boundaries[self.current_full_word]
        word_end = self.word_boundaries[self.current_full_word + 1]
        self.current_full_word += 1
        return self.agg(self.subwords[word_start:word_end])


def is_terminal_subtoken(subtoken: str, use_token_end_chars: bool = True) -> bool:
    if not use_token_end_chars:
        raise NotImplemented("Finding out if a subtoken is terminal for tokens represented with <w> and </w> tokens "
                             "is not yet implemented.")

    return subtoken.endswith(placeholders['compound_word_end'])
