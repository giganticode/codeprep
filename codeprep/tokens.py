from abc import ABC, abstractmethod
from typing import Iterator, Sequence, Any, Callable, List, Optional, Union, Type, Tuple

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
class TokenSequence(ABC):
    """
    This class incapsulates splitting full tokens into sub-tokens and contains a list of sub-tokes
    and metadata associated with it (token types, full_token boundaries):

    `TokenSequence` creation
    =============
    >>> class TypeA(object): pass
    >>> token_seq = TokenSequence.of(['hi</t>', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]), full_token_view=True)
    >>> token_seq
    [['hi</t>'], ['the', 're</t>']]

    Metadata can be accessed via object's `metadata` field:
    >>> token_seq.metadata
    ([1, 2], ['TypeA', 'TypeA'])

    When manually creating TokenSequence, sub-tokens and metadata must be in sync:
    >>> TokenSequence.of(['h', 'i</t>'], PreppedTokenMetadata([1], [TypeA]))
    Traceback (most recent call last):
    ...
    ValueError: Tokens and metadata are out-of-sync.
    The subword list has 2 elements but the number of sub-tokens according to metadata is 1.

    >>> TokenSequence.of(['hi', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]), word_end_token_added=True)
    Traceback (most recent call last):
    ...
    AssertionError: Token hi according to metadata is end-token, however it doesn't contain </t>.

    >>> token_seq.sub_token_view()
    ['hi</t>', 'the', 're</t>']

    By default each full token is returned by a list of subtokens, to change this, pass a formatting function to `format` method:
    >>> token_seq.with_format(lambda s: "".join(s))
    ['hi</t>', 'there</t>']

    Full token and sub-token views will have different length:
    >>> len(token_seq.full_token_view())
    2
    >>> len(token_seq.sub_token_view())
    3

    Indexing
    ===========
    Full-token view indexing. The result is always a full-token-view.
    >>> token_seq = TokenSequence.of(['hi</t>', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]), formatter=lambda s: "".join(s))
    >>> token_seq_full = token_seq.full_token_view()
    >>> token_seq_full[0]
    ['hi</t>']
    >>> token_seq_full[1]
    ['there</t>']
    >>> token_seq_full[2]
    []
    >>> token_seq_full[0:]
    ['hi</t>', 'there</t>']
    >>> token_seq_full[-1:]
    ['there</t>']

    Sub-token view indexing:
    >>> token_seq_sub = token_seq.sub_token_view()
    >>> token_seq_sub[0]
    ['hi</t>']
    >>> token_seq_sub[1:]
    ['the', 're</t>']
    >>> token_seq_sub[:]
    ['hi</t>', 'the', 're</t>']
    >>> token_seq_sub[0:10]
    ['hi</t>', 'the', 're</t>']

    When indexing/slicing a copy of the sequence is created:
    >>> token_seq = TokenSequence.of(['hi</t>', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]), formatter=lambda s: "".join(s))
    >>> token_seq_sub = token_seq.sub_token_view()
    >>> token_seq_full = token_seq.full_token_view()
    
    >>> token_seq_copy = token_seq[:]
    >>> token_seq_copy.tokens[0] = 'bye</t>'
    >>> token_seq_copy
    ['bye</t>', 'there</t>']
    >>> token_seq
    ['hi</t>', 'there</t>']

    Accessing single subtoken:
    >>> single_sub_token = token_seq.sub_token_view()[0]
    >>> single_sub_token.token_str()
    'hi</t>'
    >>> single_sub_token.metadata.n_subtokens(), single_sub_token.metadata.token_type()
    (1, <class 'codeprep.tokens.TypeA'>)


    Incomplete sequences
    >>> token_seq_sub[0:2]
    ['hi</t>', 'the']
    >>> incomplete_seq = token_seq_sub[0:2]
    >>> incomplete_seq.is_complete()
    False
    >>> len(incomplete_seq)
    2
    >>> len(incomplete_seq.full_token_view())
    2

    Assigning also works

    >>> token_seq_full[1] = 'Bill'
    Traceback (most recent call last):
    ...
    TypeError: Can assign only TokenSequence instance
    >>> token_seq_full[1] = token_seq_full[0]
    >>> token_seq_full
    ['hi</t>', 'hi</t>']

    Concatenation
    ===========
    >>> token_seq = TokenSequence.of(['hi</t>', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]), formatter=lambda s: "".join(s))
    >>> token_seq_sub = token_seq.sub_token_view()
    >>> token_seq_full = token_seq_sub.full_token_view()

    >>> token_seq_full + TokenSequence.empty()
    ['hi</t>', 'there</t>']
    >>> token_seq_full + token_seq_sub
    ['hi</t>', 'there</t>', 'hi</t>', 'there</t>']

    Incomplete sequences can be reassembled into complete sequences:
    >>> token_seq_sub[0:2].is_complete()
    False
    >>> incomplete_single_elm_seq = token_seq_sub[2]
    >>> incomplete_single_elm_seq.is_complete()
    False
    >>> incomplete_single_elm_seq[0].is_complete()
    False
    >>> inc_t = TokenSequence.of(['a', 'b', 'c', 'd</t>'], PreppedTokenMetadata([4], [TypeA]), full_token_view=False)[:-1]
    >>> inc_t[:].is_complete()
    False
    >>> inc_t[:-1].is_complete()
    False
    >>> inc_t[0:0].is_complete()
    True
    >>> token_seq_sub[0:2] + token_seq_sub[2]
    ['hi</t>', 'the', 're</t>']
    >>> (token_seq_sub[0:2] + token_seq_sub[2]).is_complete()
    True

    Pay attention:
    >>> token_seq_sub[0] + token_seq_sub[2]
    Traceback (most recent call last):
    ...
    ValueError: Cannot concat these token sequences


    Iteration over an external collection related to a `TokenSequence`
    ===========
    >>> token_seq = TokenSequence.of(['hi</t>', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]))
    >>> token_seq_sub = token_seq.sub_token_view()
    >>> token_seq_full = token_seq_sub.full_token_view()
    
    >>> iterator = token_seq_sub.get_iterator([1, 2], over_full_tokens=True)
    >>> [x for x in iterator]
    [1, 2, 2]
    >>> iterator = token_seq_sub.get_iterator([1, 2, 3], over_full_tokens=False)
    >>> [x for x in iterator]
    [1, 2, 3]
    >>> iterator = token_seq_full.get_iterator([1, 2], over_full_tokens=True)
    >>> [x for x in iterator]
    [1, 2]
    >>> iterator = token_seq_full.get_iterator([1, 2, 3], over_full_tokens=False)
    >>> [x for x in iterator]
    [[1], [2, 3]]


    """
    tokens: List[str]
    metadata: PreppedTokenMetadata

    word_end_token_added: bool
    return_metadata: bool = field(compare=False)
    formatter: Callable[[List[str]], Any]

    starts_with_incomplete_token: bool
    ends_with_incomplete_token: bool

    def __post_init__(self):
        if not isinstance(self.tokens, list):
            raise AssertionError()
        n_subtokens_per_token = self.metadata.n_subtokens_per_token
        if len(self.tokens) != sum(n_subtokens_per_token):
            raise ValueError(f"Tokens and metadata are out-of-sync.\n"
                             f"The subword list has {len(self.tokens)} elements but "
                             f"the number of sub-tokens according to metadata is {sum(n_subtokens_per_token)}.")
        if self.word_end_token_added:
            token_seq_full = _FullOverSubTokenIterator(self.tokens, self.metadata, formatter=lambda l: "".join(l))
            full_token_without_end_token = None
            for ind, full_token in enumerate(token_seq_full):
                if full_token_without_end_token:
                    raise AssertionError(f'Token {full_token_without_end_token} according to metadata is end-token, however it doesn\'t contain </t>.')
                if not is_terminal_subtoken(full_token):
                    full_token_without_end_token = full_token
                    if not self.ends_with_incomplete_token:
                        raise AssertionError(f'Token {full_token} according to metadata is end-token, however it doesn\'t contain </t>.')
    
        self._full_to_sub_token_indices = [0] + list(cum_sum(self.metadata.n_subtokens_per_token))
        self._sub_to_full_token_indices = {n: i for i, n in enumerate(self._full_to_sub_token_indices)}

    @staticmethod
    def of(tokens: List[str] = None, metadata: PreppedTokenMetadata = None,
           full_token_view: bool = True,
           word_end_token_added: bool = True,
           return_metadata: bool = False,
           formatter=lambda x:x,
           starts_with_incomplete_token: bool = False,
           ends_with_incomplete_token: bool = False) -> 'TokenSequence':
        tokens = tokens or []
        metadata = metadata or PreppedTokenMetadata()
        sequence_type = FullTokenSequence if full_token_view else SubTokenSequence
        return sequence_type(tokens, metadata, word_end_token_added=word_end_token_added,
                                          return_metadata=return_metadata,
                                          formatter=formatter,
                                          starts_with_incomplete_token=starts_with_incomplete_token,
                                          ends_with_incomplete_token=ends_with_incomplete_token)

    @staticmethod
    def as_sequence(token_seq: 'TokenSequence', **kwargs) -> 'TokenSequence':
        return token_seq.shallow_copy(type(token_seq), **kwargs)

    @staticmethod
    def empty(full_token_view: bool = True) -> 'TokenSequence':
        return TokenSequence.of(full_token_view=True) if full_token_view else TokenSequence.of(full_token_view=False)

    def is_complete(self) -> bool:
        return not self.starts_with_incomplete_token and not self.ends_with_incomplete_token

    def shallow_copy(self, new_type, **kwargs) -> 'TokenSequence':
        dict_copy = {k:v for k, v in self.__dict__.items() if k in self.__dataclass_fields__}
        dict_copy.update(kwargs)
        return new_type(**dict_copy)

    def __add__(self, other):
        return self.add(other)

    def add(self, other: 'TokenSequence') -> 'TokenSequence':
        if not isinstance(other, TokenSequence):
            raise TypeError(f'Cannot add {type(other)} to a {type(self)}.')

        resulting_tokens = self.tokens + other.tokens
        if not self.ends_with_incomplete_token and not other.starts_with_incomplete_token:
            resulting_metadata = self.metadata + other.metadata
        elif self.ends_with_incomplete_token and other.starts_with_incomplete_token and self.metadata.token_types[-1] == other.metadata.token_types[0]:
            n_subtokens_in_merged_tokens = self.metadata.n_subtokens_per_token[-1] + other.metadata.n_subtokens_per_token[0]
            incomplete_chunk_between = PreppedTokenMetadata([n_subtokens_in_merged_tokens], [self.metadata.token_types[-1]])
            resulting_metadata = self.metadata[:-1] + incomplete_chunk_between + other.metadata[1:]
        else:
            raise ValueError("Cannot concat these token sequences")

        return TokenSequence.of(resulting_tokens, resulting_metadata,
                                full_token_view=not isinstance(self, SubTokenSequence),
                                word_end_token_added=self.word_end_token_added,
                                return_metadata=self.return_metadata,
                                formatter=self.formatter,
                                starts_with_incomplete_token=self.starts_with_incomplete_token,
                                ends_with_incomplete_token=other.ends_with_incomplete_token)

    def token_str(self) -> str:
        if len(self.tokens) != 1:
            raise ValueError("This method can be only called if the sequence contains only one token.")

        return self.tokens[0]

    @abstractmethod
    def __iter__(self) -> Union[Iterator[str], Iterator['TokenSequence']]:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    def __repr__(self):
        return repr([i for i in self.shallow_copy(type(self), return_metadata=False)])

    def full_token_view(self, **kwargs) -> 'TokenSequence':
        if type(self) == FullTokenSequence and not kwargs:
            return self
        return self.shallow_copy(FullTokenSequence, **kwargs)

    def sub_token_view(self, **kwargs) -> 'TokenSequence':
        if type(self) == SubTokenSequence and not kwargs:
            return self
        return self.shallow_copy(SubTokenSequence, **kwargs)

    @abstractmethod
    def get_iterator(self, over, over_full_tokens: bool, formatter: Callable[[List[str]], Any]) -> Iterator:
        pass

    def without_metadata(self) -> 'TokenSequence':
        return self.shallow_copy(type(self), return_metadata=False)

    def with_metadata(self) -> 'TokenSequence':
        return self.shallow_copy(type(self), return_metadata=True)

    def with_format(self, formatter: Callable[[List[str]], Any]) -> 'TokenSequence':
        return self.shallow_copy(type(self), formatter=formatter)

    @abstractmethod
    def __getitem__(self, item: Union[int, slice]) -> 'TokenSequence':
        pass

    def _normilize_index(self, index: Optional[int]) -> Optional[int]:
        if index is None:
            return None

        n_full_tokens = len(self)
        if index < - n_full_tokens:
            raise KeyError(index)

        if - n_full_tokens <= index < 0:
            return n_full_tokens + index

        if index > n_full_tokens:
            return n_full_tokens

        return index

    def _full_to_sub_index(self, index: Optional[int]) -> Optional[int]:
        if index is None:
            return index
        return self._full_to_sub_token_indices[index]

    def _sub_to_full_index(self, index: Optional[int]) -> Optional[int]:
        if index is None:
            return index
        try:
            return self._sub_to_full_token_indices[index]
        except KeyError:
            raise KeyError(f"Sub-index {index} is in the middle of a full-tokens")

    def _sub_to_adjusted_full_index(self, index: int, to_left: bool):
        if index is None:
            return None

        while index not in self._sub_to_full_token_indices:
            if to_left:
                index -= 1
            else:
                index += 1
        return self._sub_to_full_token_indices[index]

    def _normalized_passed_index(self, item: Union[int, slice]) -> Tuple[int, int]:
        if isinstance(item, int):
            start = item
            stop = item + 1
        elif isinstance(item, slice):
            if item.step is not None:
                raise NotImplemented("It is not possible to specify step")
            start = item.start
            stop = item.stop
        else:
            raise TypeError()

        start = self._normilize_index(start)
        stop = self._normilize_index(stop)

        return start, stop


@dataclass(repr=False)
class SubTokenSequence(TokenSequence):
    def __iter__(self) -> Union[Iterator[str], Iterator[TokenSequence]]:
        if self.return_metadata:
            return iter([self[i] for i in range(len(self))])
        else:
            return iter(self.tokens)

    def __getitem__(self, item: Union[int, slice]):
        start, stop = self._normalized_passed_index(item)

        adjusted_before = 0
        adjusted_after = 0
        try:
            full_start = self._sub_to_full_index(start)
        except KeyError:
            full_start = self._sub_to_adjusted_full_index(start, to_left=True)
            adjusted_before = start - self._full_to_sub_index(full_start)
        try:
            full_stop = self._sub_to_full_index(stop)
        except KeyError:
            full_stop = self._sub_to_adjusted_full_index(stop, to_left=False)
            adjusted_after = self._full_to_sub_index(full_stop) - stop

        n_subtokens = self.metadata.n_subtokens_per_token[full_start:full_stop]
        if adjusted_before > 0:
            n_subtokens[0] -= adjusted_before
        if adjusted_after > 0:
            n_subtokens[-1] -= adjusted_after

        metadata = PreppedTokenMetadata(
            n_subtokens,
            self.metadata.token_types[full_start:full_stop]
        )

        starts_with_incomplete_token = (adjusted_before > 0) or ((start == 0 or start is None) and self.starts_with_incomplete_token)
        ends_with_incomplete_token = (adjusted_after > 0) or ((stop == len(self.tokens) or stop is None) and self.ends_with_incomplete_token)

        return self.shallow_copy(new_type=type(self), tokens=self.tokens[start:stop], metadata=metadata,
                                     starts_with_incomplete_token=starts_with_incomplete_token,
                                     ends_with_incomplete_token=ends_with_incomplete_token)

    def __len__(self):
        return len(self.tokens)

    def get_iterator(self, over, over_full_tokens: bool, formatter: Callable[[List[str]], Any] = lambda x: x) -> Iterator:
        return _SubOverFullTokenIterator(over, self.metadata) if over_full_tokens else iter(over)

    @classmethod
    def from_full_token(cls, prepped_token: List[str], token_type: Type):
        return cls(prepped_token, PreppedTokenMetadata([len(prepped_token)], [token_type]))


@dataclass(repr=False)
class FullTokenSequence(TokenSequence):
    def __iter__(self) -> Union[Iterator[str], Iterator['TokenSequence']]:
        over = self.sub_token_view() if self.return_metadata else self.tokens
        formatter = (lambda x: x) if self.return_metadata else self.formatter
        return _FullOverSubTokenIterator(over, metadata=self.metadata, formatter=formatter)

    def get_iterator(self, over: Sequence[Any], over_full_tokens: bool, formatter: Callable[[List[str]], Any] = lambda x: x) -> Iterator:
        return iter(over) if over_full_tokens else _FullOverSubTokenIterator(over, metadata=self.metadata, formatter=formatter)

    def __setitem__(self, key, value):
        if not isinstance(value, FullTokenSequence):
            raise TypeError("Can assign only TokenSequence instance")

        self.__dict__ = self[:key].add(value).add(self[key + 1:]).__dict__

    def __getitem__(self, item: Union[int, slice]):
        start, stop = self._normalized_passed_index(item)

        full_item = slice(
            self._full_to_sub_index(start),
            self._full_to_sub_index(stop),
            1,
        )
        starts_with_incomplete_token = self.starts_with_incomplete_token and (start==0 or start is None)
        ends_with_incomplete_token = self.ends_with_incomplete_token and (stop==len(self) or stop is None)
        return self.shallow_copy(new_type=type(self), tokens=self.tokens[full_item],
                                    metadata=PreppedTokenMetadata(
                                        self.metadata.n_subtokens_per_token[start:stop],
                                        self.metadata.token_types[start:stop]
                                    ), starts_with_incomplete_token=starts_with_incomplete_token,
                                 ends_with_incomplete_token=ends_with_incomplete_token)

    def __len__(self):
        return self._sub_to_full_token_indices[len(self.tokens)]


def is_terminal_subtoken(subtoken: str, use_token_end_chars: bool = True) -> bool:
    if not use_token_end_chars:
        raise NotImplemented("Finding out if a subtoken is terminal for tokens represented with <w> and </w> tokens "
                             "is not yet implemented.")

    return subtoken.endswith(placeholders['compound_word_end']) or subtoken == '`pad'