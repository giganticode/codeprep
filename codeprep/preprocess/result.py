from typing import List, Set, Iterator, Any, Callable, Union, Type, Optional, Iterable

import numpy as np
from dataclasses import dataclass, field

from codeprep.preprocess.metadata import PreppedTokenMetadata
from codeprep.preprocess.placeholders import placeholders


class _SubOverFullTokenIterator(Iterator):
    def __init__(self, over: Iterable[Any],
                 metadata: PreppedTokenMetadata):
        self.over = over
        self.metadata = metadata

        self.current_full_word = 0
        self.current_index = 0

    def __next__(self):
        if self.current_full_word >= len(self.over):
            raise StopIteration

        result = self.over[self.current_full_word]

        self.current_index += 1
        if self.current_index >= self.metadata.n_subtokens_per_token[self.current_full_word]:
            self.current_index = 0
            self.current_full_word += 1

        return result


class _FullOverSubTokenIterator(Iterator):
    def __init__(self, over: Iterable[Any],
                 metadata: PreppedTokenMetadata,
                 formatter: Callable[[List[Any]], Any] = lambda x: x):
        self.over = over
        self.metadata = metadata
        self.formatter = formatter

        self.current_full_word = 0
        self.current_index = 0

    def __next__(self):
        if self.current_full_word >= len(self.metadata.n_subtokens_per_token):
            raise StopIteration

        sub_words_in_current_full_word = self.metadata.n_subtokens_per_token[self.current_full_word]
        formatted_value = self.formatter(self.over[self.current_index:self.current_index + sub_words_in_current_full_word])
        result = formatted_value

        self.current_full_word += 1
        self.current_index += sub_words_in_current_full_word

        return result


@dataclass
class SurrogatePreppedTokenSequence(object):
    tokens: List[str]

    def add(self, other: 'PreppedTokenSequence') -> 'SurrogatePreppedTokenSequence':
        if isinstance(other, SurrogatePreppedTokenSequence):
            return SurrogatePreppedTokenSequence(self.tokens + other.tokens)
        else:
            raise TypeError()


@dataclass
class PreppedTokenSequence(object):
    """
    >>> class TypeA(object): pass
    >>> PreppedSubTokenSequence(['h', 'i</t>'], PreppedTokenMetadata([1], [TypeA]))
    Traceback (most recent call last):
    ...
    ValueError: Tokens and metadata are out-of-sync.
    The subword list has 2 elements but the number of sub-tokens according to metadata is 1.
    >>> prepped_tokens = PreppedSubTokenSequence(['hi</t>', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]))
    >>> prepped_tokens
    ['hi</t>', 'the', 're</t>']
    >>> len(prepped_tokens)
    3
    >>> prepped_tokens.full_tokens_view()
    [['hi</t>'], ['the', 're</t>']]
    >>> full_prepped_tokens = prepped_tokens.full_tokens_view(formatter=lambda x: "".join(x))
    >>> full_prepped_tokens
    ['hi</t>', 'there</t>']
    >>> len(full_prepped_tokens)
    2
    >>> full_prepped_tokens[:]
    ['hi</t>', 'there</t>']
    >>> full_prepped_tokens[0:2]
    ['hi</t>', 'there</t>']
    >>> full_prepped_tokens[-10:10]
    ['hi</t>', 'there</t>']
    >>> full_prepped_tokens[:-1]
    ['hi</t>']
    >>> full_prepped_tokens[1:]
    ['there</t>']
    >>> full_prepped_tokens[1:1]
    []
    >>> full_prepped_tokens[-2:0]
    []
    >>> full_prepped_tokens[-2:]
    ['hi</t>', 'there</t>']
    >>> full_prepped_tokens[-1:]
    ['there</t>']
    """
    tokens: List[Any] = field(default_factory=list)
    metadata: PreppedTokenMetadata = field(default_factory=PreppedTokenMetadata)
    word_end_token_added: bool = False

    def __post_init__(self):
        assert isinstance(self.tokens, list)
        n_subtokens_per_token = self.metadata.n_subtokens_per_token
        if len(self.tokens) != sum(n_subtokens_per_token):
            raise ValueError(f"Tokens and metadata are out-of-sync.\n"
                             f"The subword list has {len(self.tokens)} elements but "
                             f"the number of sub-tokens according to metadata is {sum(n_subtokens_per_token)}.")
        if self.word_end_token_added:
            full_tokens = _FullOverSubTokenIterator(self.tokens, self.metadata, formatter=lambda l: "".join(l))
            for ind, full_token in enumerate(full_tokens):
                if not is_terminal_subtoken(full_token):
                    raise AssertionError(f'Token {full_token} according to metadata is end-token, however it doesn\'t contain </t>. '
                                         f'Showing context: {full_tokens[(ind-20) if ind > 20 else 0:ind]}')

        self._full_to_sub_token_indices = [0] + list(np.cumsum(self.metadata.n_subtokens_per_token))
        self._sub_to_full_token_indices = {n: i for i, n in enumerate(self._full_to_sub_token_indices)}

    def _convert_index(self, index: Optional[int], conversion_func: Callable[[int], int]) -> Optional[int]:
        if index is None:
            return None

        n_full_tokens = len(self)
        if index < - n_full_tokens:
            return - self._convert_index(n_full_tokens + 1, conversion_func) - 1

        if - n_full_tokens <= index < 0:
            return self._convert_index(n_full_tokens + index, conversion_func)

        if index > n_full_tokens:
            return self._convert_index(n_full_tokens, conversion_func)

        return conversion_func(index)

    def _full_to_sub_index(self, index: Optional[int]) -> Optional[int]:
        return self._convert_index(index, lambda i: self._full_to_sub_token_indices[i])

    def _sub_to_full_index(self, index: Optional[int]) -> Optional[int]:
        def conversion_func(ind: int) -> int:
            try:
                return self._sub_to_full_token_indices[ind]
            except KeyError:
                raise KeyError(f"Sub-index {ind} is in the middle of a full-tokens")

        return self._convert_index(index, conversion_func)

    def full_tokens_view(self, formatter: Callable[[List[Any]], List[Any]] = lambda x: x, return_token_type: bool = False) -> 'PreppedFullTokenSequence':
        return PreppedFullTokenSequence(
            self.tokens,
            self.metadata,
            word_end_token_added=self.word_end_token_added,
            formatter=formatter,
            return_token_type=return_token_type
        )

    def sub_token_view(self) -> 'PreppedSubTokenSequence':
        return PreppedSubTokenSequence(
            self.tokens,
            self.metadata,
            word_end_token_added=self.word_end_token_added
        )

    def __str__(self):
        return repr([i for i in self])

    def add(self, other: 'PreppedTokenSequence') -> Union['PreppedTokenSequence', SurrogatePreppedTokenSequence]:
        if isinstance(other, PreppedTokenSequence):
            self.tokens.extend(other.tokens)
            self.metadata.update_(other.metadata)
            return self
        elif isinstance(other, SurrogatePreppedTokenSequence):
            return SurrogatePreppedTokenSequence(self.tokens + other.tokens)
        else:
            raise TypeError()


@dataclass
class PreppedSubTokenSequence(PreppedTokenSequence):
    def __iter__(self) -> Iterator[str]:
        return iter(self.tokens)

    def __getitem__(self, item):
        if not isinstance(item, slice):
            item = slice(item, item + 1, 1)
        elif item.step is not None:
            raise NotImplemented("It is not possible to specify step")

        try:
            full_index = slice(
                self._sub_to_full_index(item.start),
                self._sub_to_full_index(item.stop),
                1,
            )
            return PreppedSubTokenSequence(self.tokens[item],
                                           PreppedTokenMetadata(
                                               self.metadata.n_subtokens_per_token[full_index],
                                               self.metadata.token_types[full_index]
                                           ), word_end_token_added=self.word_end_token_added)
        except KeyError:
            return SurrogatePreppedTokenSequence(self.tokens[item])


    def __repr__(self):
        return repr([i for i in self])

    def __len__(self):
        return len(self.tokens)

    def get_iterator(self, over, over_full_tokens: bool):
        return _SubOverFullTokenIterator(over, self.metadata) if over_full_tokens else iter(over)

    @classmethod
    def from_full_token(cls, prepped_token: List[str], token_type: Type):
        return cls(prepped_token, PreppedTokenMetadata([len(prepped_token)], [token_type]))

    def set_all_tokens_type(self, t: Type) -> None:
        self.metadata.token_types = [t] * len(self.metadata.n_subtokens_per_token)


@dataclass
class PreppedFullTokenSequence(PreppedTokenSequence):
    formatter: Callable[[List[Any]], Any] = field(default_factory=lambda: lambda x: x)
    return_token_type: bool = False

    def __iter__(self) -> Union[Iterator[str], Iterator['PreppedFullTokenSequence']]:
        token_iterator = _FullOverSubTokenIterator(self.tokens, self.metadata, self.formatter)
        return iter(zip(token_iterator, self.metadata.token_types)) if self.return_token_type else token_iterator

    def get_iterator(self, over: Iterable[Any], over_full_tokens: bool, formatter: Callable = lambda x: x):
        return iter(over) if over_full_tokens else _FullOverSubTokenIterator(over, self.metadata, formatter)

    def __getitem__(self, item: Union[int, slice]):
        if not isinstance(item, slice):
            item = slice(item, item + 1, 1)
        elif item.step is not None:
            raise NotImplemented("It is not possible to specify step")

        full_item = slice(
            self._full_to_sub_index(item.start),
            self._full_to_sub_index(item.stop),
            1,
        )
        return PreppedFullTokenSequence(self.tokens[full_item],
                                    PreppedTokenMetadata(
                                        self.metadata.n_subtokens_per_token[item],
                                        self.metadata.token_types[item]
                                    ), word_end_token_added=self.word_end_token_added, formatter=self.formatter, return_token_type=self.return_token_type)

    def __len__(self):
        return self._sub_to_full_token_indices[len(self.tokens)]

    def __repr__(self):
        return repr([i for i in self])


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


def insert_word_end_tokens_(self) -> 'PreppedSubTokenSequence':
    assert not self.word_end_token_added
    new_tokens = []
    for subtokens in self.full_tokens_view(formatter=lambda x: x[:-1] + [x[-1] + placeholders['compound_word_end']]):
        new_tokens.extend(subtokens)
    return PreppedSubTokenSequence(new_tokens, self.metadata, word_end_token_added=True)


def is_terminal_subtoken(subtoken: str, use_token_end_chars: bool = True) -> bool:
    if not use_token_end_chars:
        raise NotImplemented("Finding out if a subtoken is terminal for tokens represented with <w> and </w> tokens "
                             "is not yet implemented.")

    return subtoken.endswith(placeholders['compound_word_end'])