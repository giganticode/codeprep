from abc import ABC, abstractmethod
from typing import Iterator, Sequence, Any, Callable, List, Optional, Union, Type, Iterable

from dataclasses import dataclass, field

from codeprep.preprocess.metadata import PreppedTokenMetadata
from codeprep.preprocess.placeholders import placeholders
from codeprep.util.misc import cum_sum


class _SubOverFullTokenIterator(Iterator):
    def __init__(self, over: Sequence[Any],
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
    def __init__(self, over: Sequence[Any],
                 metadata: PreppedTokenMetadata,
                 formatter: Callable[[Sequence[Any]], Any] = lambda x: x):
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
    metadata: Optional[PreppedTokenMetadata] = None

    def add(self, other: 'PreppedTokenSequence') -> 'SurrogatePreppedTokenSequence':
        if self.metadata is not None:
            raise TypeError('Cannot add SurrogatePreppedTokenSequences when metadata is present.')
        if isinstance(other, SurrogatePreppedTokenSequence):
            return SurrogatePreppedTokenSequence(self.tokens + other.tokens)
        else:
            raise TypeError()

    def __add__(self, other):
        return self.add(other)


@dataclass
class PreppedTokenSequence(ABC):
    """
    >>> class TypeA(object): pass
    >>> PreppedSubTokenSequence(['h', 'i</t>'], PreppedTokenMetadata([1], [TypeA]))
    Traceback (most recent call last):
    ...
    ValueError: Tokens and metadata are out-of-sync.
    The subword list has 2 elements but the number of sub-tokens according to metadata is 1.
    >>> prepped_tokens = PreppedSubTokenSequence(['hi', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]), word_end_token_added=True)
    Traceback (most recent call last):
    ...
    AssertionError: Token hi according to metadata is end-token, however it doesn't contain </t>.
    >>> prepped_tokens = PreppedSubTokenSequence(['hi</t>', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]), word_end_token_added=True, formatter=lambda x:x)
    >>> prepped_tokens
    ['hi</t>', 'the', 're</t>']
    >>> len(prepped_tokens)
    3
    >>> prepped_tokens.full_tokens_view()
    [['hi</t>'], ['the', 're</t>']]
    >>> full_prepped_tokens = prepped_tokens.full_tokens_view(formatter=lambda x: "".join(x))
    >>> full_prepped_tokens
    ['hi</t>', 'there</t>']
    >>> sub_prepped_tokens = full_prepped_tokens.sub_token_view()
    >>> sub_prepped_tokens
    ['hi</t>', 'the', 're</t>']
    >>> len(sub_prepped_tokens)
    3
    >>> sub_prepped_tokens[0]
    ['hi</t>']
    >>> sub_prepped_tokens[1]
    SurrogatePreppedTokenSequence(tokens=['the'], metadata=None)
    >>> (sub_prepped_tokens[0] + sub_prepped_tokens[1:]).full_tokens_view()
    ['hi</t>', 'there</t>']
    >>> sub_prepped_tokens[0] + sub_prepped_tokens[1] + sub_prepped_tokens[2:]
    SurrogatePreppedTokenSequence(tokens=['hi</t>', 'the', 're</t>'], metadata=None)
    >>> [i for i in sub_prepped_tokens.with_metadata()]
    [SurrogatePreppedTokenSequence(tokens='hi</t>', metadata=([1], ['TypeA'])), SurrogatePreppedTokenSequence(tokens='the', metadata=([2], ['TypeA'])), SurrogatePreppedTokenSequence(tokens='re</t>', metadata=([2], ['TypeA']))]
    >>> len(full_prepped_tokens)
    2
    >>> full_prepped_tokens[:]
    ['hi</t>', 'there</t>']
    >>> full_prepped_tokens[0:2]
    ['hi</t>', 'there</t>']
    >>> full_prepped_tokens[-10:10]
    ['hi</t>', 'there</t>']
    >>> elm = full_prepped_tokens[:-1]
    >>> elm
    ['hi</t>']
    >>> elm.token_str()
    'hi</t>'
    >>> elm.metadata.n_subtokens(), elm.metadata.token_type()
    (1, <class 'codeprep.tokens.TypeA'>)
    >>> elm.tokens[0] = 'bye</t>'
    >>> full_prepped_tokens
    ['hi</t>', 'there</t>']
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
    >>> full_prepped_tokens[1] = 'Bill'
    Traceback (most recent call last):
    ...
    TypeError: Can assign only PreppedFullTokenSequence instance
    >>> full_prepped_tokens[1] = full_prepped_tokens[0]
    >>> full_prepped_tokens
    ['hi</t>', 'hi</t>']
    >>> full_prepped_tokens.tokens[0] = 'bye</t>'
    >>> full_prepped_tokens
    ['bye</t>', 'hi</t>']

    Iteration over an external collection related to a `PreppedTokenSequence`
    >>> [x for x in sub_prepped_tokens.get_iterator([1, 2], over_full_tokens=True)]
    [1, 2, 2]
    >>> [x for x in sub_prepped_tokens.get_iterator([1, 2, 3], over_full_tokens=False)]
    [1, 2, 3]
    >>> full_prepped_tokens = sub_prepped_tokens.full_tokens_view()
    >>> [x for x in full_prepped_tokens.get_iterator([1, 2], over_full_tokens=True)]
    [1, 2]
    >>> [x for x in full_prepped_tokens.get_iterator([1, 2, 3], over_full_tokens=False)]
    [[1], [2, 3]]
    """
    tokens: List[Any] = field(default_factory=list)
    metadata: PreppedTokenMetadata = field(default_factory=PreppedTokenMetadata)
    word_end_token_added: bool = False
    return_metadata: bool = field(default=False, compare=False)
    formatter: Callable[[List[Any]], Any] = field(default_factory=lambda: lambda x: x, compare=False)

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
                    raise AssertionError(f'Token {full_token} according to metadata is end-token, however it doesn\'t contain </t>.')

        self._full_to_sub_token_indices = [0] + list(cum_sum(self.metadata.n_subtokens_per_token))
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

    def full_tokens_view(self, **kwargs) -> 'PreppedFullTokenSequence':
        return self.shallow_copy(PreppedFullTokenSequence, **kwargs)

    def sub_token_view(self, **kwargs) -> 'PreppedSubTokenSequence':
        return self.shallow_copy(PreppedSubTokenSequence, **kwargs)

    def shallow_copy(self, new_type, **kwargs) -> Union['PreppedSubTokenSequence', 'PreppedFullTokenSequence']:
        dict_copy = {k:v for k, v in self.__dict__.items() if k in self.__dataclass_fields__}
        dict_copy.update(kwargs)
        return new_type(**dict_copy)

    def __repr__(self):
        return repr([i for i in self.shallow_copy(type(self), return_metadata=False)])

    def add(self, other: 'PreppedTokenSequence') -> Union['PreppedTokenSequence', SurrogatePreppedTokenSequence]:
        if isinstance(other, PreppedTokenSequence):
            self.tokens.extend(other.tokens)
            self.metadata.update_(other.metadata)
            return self.shallow_copy(type(self), tokens=self.tokens, metadata=self.metadata)
        elif isinstance(other, SurrogatePreppedTokenSequence):
            return SurrogatePreppedTokenSequence(self.tokens + other.tokens)
        else:
            raise TypeError()

    @staticmethod
    def empty(full_tokens: bool) -> Union['PreppedSubTokenSequence', 'PreppedFullTokenSequence']:
        return PreppedFullTokenSequence() if full_tokens else PreppedSubTokenSequence()

    def __add__(self, other):
        return self.add(other)

    def token_str(self) -> str:
        if len(self.tokens) != 1:
            raise ValueError("This method can be only called if the sequence contains only one token.")

        return self.tokens[0]

    @abstractmethod
    def __iter__(self) -> Union[Iterator[SurrogatePreppedTokenSequence], Iterator['PreppedFullTokenSequence'], Iterator['PreppedSubTokenSequence']]:
        pass

    @abstractmethod
    def get_iterator(self, over, over_full_tokens: bool) -> Iterator:
        pass

    @abstractmethod
    def __getitem__(self, item: Union[int, slice]):
        pass

    def without_metadata(self):
        return self.shallow_copy(type(self), return_metadata=False)

    def with_metadata(self):
        return self.shallow_copy(type(self), return_metadata=True)


@dataclass(repr=False)
class PreppedSubTokenSequence(PreppedTokenSequence):
    def __iter__(self) -> Union[Iterator[str], Iterator[SurrogatePreppedTokenSequence]]:
        return iter(SurrogatePreppedTokenSequence(t, PreppedTokenMetadata([s], [tt])) for t, (s, tt) in zip(iter(self.tokens), _SubOverFullTokenIterator([i for i in zip(self.metadata.n_subtokens_per_token, self.metadata.token_types)], self.metadata))) if self.return_metadata else iter(self.tokens)

    def __getitem__(self, item: Union[int, slice]):
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
            return self.shallow_copy(new_type=type(self), tokens=self.tokens[item],
                                           metadata=PreppedTokenMetadata(
                                               self.metadata.n_subtokens_per_token[full_index],
                                               self.metadata.token_types[full_index]
                                           ))
        except KeyError:
            return SurrogatePreppedTokenSequence(self.tokens[item])

    def __len__(self):
        return len(self.tokens)

    def get_iterator(self, over, over_full_tokens: bool) -> Iterator:
        return _SubOverFullTokenIterator(over, self.metadata) if over_full_tokens else iter(over)

    @classmethod
    def from_full_token(cls, prepped_token: List[str], token_type: Type):
        return cls(prepped_token, PreppedTokenMetadata([len(prepped_token)], [token_type]))

    def set_all_tokens_type(self, t: Type) -> None:
        self.metadata.token_types = [t] * len(self.metadata.n_subtokens_per_token)


@dataclass(repr=False)
class PreppedFullTokenSequence(PreppedTokenSequence):
    def __iter__(self) -> Union[Iterator[str], Iterator['PreppedFullTokenSequence']]:
        over = self.sub_token_view() if self.return_metadata else self.tokens
        formatter = (lambda x: x) if self.return_metadata else self.formatter
        return _FullOverSubTokenIterator(over, metadata=self.metadata, formatter=formatter)

    def get_iterator(self, over: Sequence[Any], over_full_tokens: bool, formatter: Callable = lambda x: x) -> Iterator:
        return iter(over) if over_full_tokens else _FullOverSubTokenIterator(over, metadata=self.metadata, formatter=formatter)

    def __setitem__(self, key, value):
        if not isinstance(value, PreppedFullTokenSequence):
            raise TypeError("Can assign only PreppedFullTokenSequence instance")

        self.__dict__ = self[:key].add(value).add(self[key + 1:]).__dict__

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
        return self.shallow_copy(new_type=type(self), tokens=self.tokens[full_item],
                                    metadata=PreppedTokenMetadata(
                                        self.metadata.n_subtokens_per_token[item],
                                        self.metadata.token_types[item]
                                    ))

    def __len__(self):
        return self._sub_to_full_token_indices[len(self.tokens)]


def is_terminal_subtoken(subtoken: str, use_token_end_chars: bool = True) -> bool:
    if not use_token_end_chars:
        raise NotImplemented("Finding out if a subtoken is terminal for tokens represented with <w> and </w> tokens "
                             "is not yet implemented.")

    return subtoken.endswith(placeholders['compound_word_end'])