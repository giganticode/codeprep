# SPDX-FileCopyrightText: 2020 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Iterator, Sequence, Any, Callable, List, Union, Optional, Tuple, Mapping

from dataclasses import dataclass, field

from codeprep.preprocess.metadata import PreppedTokenMetadata
from codeprep.preprocess.placeholders import placeholders
from codeprep.util.misc import cum_sum


class _FullToSubTokenIterator(Iterator):
    """
    Iterator that walks through values aligned with full tokens and returns values aligned with subtokens
    >>> it = _FullToSubTokenIterator([1, 1], metadata=PreppedTokenMetadata([2], [None]))
    Traceback (most recent call last):
    ...
    ValueError: The sequence to be iterated over must equal to the number of full tokens.

    >>> it = _FullToSubTokenIterator([1, 2, 3], metadata=PreppedTokenMetadata([1, 2, 1], [None, None, None]))
    >>> [t for t in it]
    [1, 2, 2, 3]
    """
    def __init__(self, over: Sequence[Any],
                 metadata: PreppedTokenMetadata):
        if len(over) != len(metadata):
            raise ValueError('The sequence to be iterated over must equal to the number of full tokens.')

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


class _SubToFullTokenIterator(Iterator):
    """
    Iterator that walks through values aligned with sub-tokens and returns values aligned with full tokens
    >>> it = _SubToFullTokenIterator([1], metadata=PreppedTokenMetadata([2], [None]))
    Traceback (most recent call last):
    ...
    ValueError: The sequence to be iterated over must equal to the number of sub-tokens.

    >>> it = _SubToFullTokenIterator([1, 2, 2, 3], metadata=PreppedTokenMetadata([1, 2, 1], [None, None, None]))
    >>> [t for t in it]
    [[1], [2, 2], [3]]

    >>> it = _SubToFullTokenIterator([1, 2, 2, 3],\
metadata=PreppedTokenMetadata([1, 2, 1], [None, None, None]), formatter=sum)
    >>> [t for t in it]
    [1, 4, 3]
    """
    def __init__(self, over: Sequence[Any],
                 metadata: PreppedTokenMetadata,
                 formatter: Callable[[List[Any]], Any] = lambda x: x):
        if len(over) != sum(metadata.n_subtokens_per_token):
            raise ValueError('The sequence to be iterated over must equal to the number of sub-tokens.')

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
    >>> token_seq = TokenSequence.create(['hi</t>', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]), full_token_view=True)
    >>> token_seq
    [['hi</t>'], ['the', 're</t>']]

    Metadata can be accessed via object's `metadata` field:
    >>> token_seq.metadata
    ([1, 2], ['TypeA', 'TypeA'])

    When manually creating TokenSequence, sub-tokens and metadata must be in sync:
    >>> TokenSequence.create(['h', 'i</t>'], PreppedTokenMetadata([1], [TypeA]))
    Traceback (most recent call last):
    ...
    ValueError: The sequence to be iterated over must equal to the number of sub-tokens.

    >>> token_seq.subtokens
    ['hi</t>', 'the', 're</t>']

    Full token and sub-token views will have different length:
    >>> len(token_seq.fulltokens)
    2
    >>> len(token_seq.subtokens)
    3

    Indexing
    ===========
    Full-token view indexing. The result is always a full-token-view.
    >>> token_seq = TokenSequence.create(['hi</t>', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]), formatter=lambda s: "".join(s))
    >>> token_seq.fulltokens[0]
    ['hi</t>']
    >>> token_seq.fulltokens[1]
    ['there</t>']
    >>> token_seq.fulltokens[2]
    []
    >>> token_seq.fulltokens[0:]
    ['hi</t>', 'there</t>']
    >>> token_seq.fulltokens[-1:]
    ['there</t>']
    >>> token_seq.fulltokens[-1]
    ['there</t>']

    Sub-token view indexing:
    >>> token_seq.subtokens[0]
    ['hi</t>']
    >>> token_seq.subtokens[1:]
    ['the', 're</t>']
    >>> token_seq.subtokens[:]
    ['hi</t>', 'the', 're</t>']
    >>> token_seq.subtokens[0:10]
    ['hi</t>', 'the', 're</t>']

    When indexing/slicing a copy of the sequence is created:
    # TODO think if the 'view' functionality is needed for efficiency
    >>> token_seq = TokenSequence.create(['hi</t>', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]), formatter=lambda s: "".join(s))
    >>> token_seq_sub = token_seq.subtokens
    >>> token_seq_full = token_seq.fulltokens

    >>> token_seq_copy = token_seq[:]
    >>> token_seq_copy._tokens[0] = 'bye</t>'
    >>> token_seq_copy
    ['bye</t>', 'there</t>']
    >>> token_seq
    ['hi</t>', 'there</t>']


    Incomplete sequences
    >>> token_seq_sub[0:2]
    ['hi</t>', 'the']
    >>> token_seq_sub[-100:-3]
    []
    >>> token_seq_sub[-100:-2]
    ['hi</t>']
    >>> token_seq_sub[-100]
    Traceback (most recent call last):
    ...
    KeyError: -100
    >>> incomplete_seq = token_seq_sub[0:2]
    >>> incomplete_seq.is_complete()
    False
    >>> len(incomplete_seq)
    2
    >>> len(incomplete_seq.fulltokens)
    2

    Assignment also works

    >>> token_seq_full[1] = 'Bill'
    Traceback (most recent call last):
    ...
    TypeError: Can assign only TokenSequence instance
    >>> token_seq_full[1] = token_seq_full[0]
    >>> token_seq_full
    ['hi</t>', 'hi</t>']

    Concatenation
    ===========
    >>> token_seq = TokenSequence.create(['hi</t>', 'the' ,'re</t>'], PreppedTokenMetadata([1, 2], [TypeA, TypeA]), formatter=lambda s: "".join(s))
    >>> token_seq_sub = token_seq.subtokens
    >>> token_seq_full = token_seq_sub.fulltokens

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
    >>> inc_t = TokenSequence.create(['a', 'b', 'c', 'd</t>'], PreppedTokenMetadata([4], [TypeA]), full_token_view=False)[:-1]
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
    >>> t = token_seq_sub[0:2]
    >>> t.extend(token_seq_sub[2] + token_seq_sub[1] + token_seq_sub[2])
    ['hi</t>', 'the', 're</t>', 'the', 're</t>']
    >>> t[:4].fulltokens[:-1]
    ['hi</t>', 'there</t>']
    >>> t[0:2].is_complete()
    False

    Pay attention:
    >>> token_seq_sub[0] + token_seq_sub[2]
    Traceback (most recent call last):
    ...
    ValueError: Cannot concat these sequences: ...['hi</t>'] and []...

    >>> token_seq_sub[0].extend(token_seq_sub[2])
    Traceback (most recent call last):
    ...
    ValueError: Cannot concat these sequences: ...['hi</t>'] and []...



    """
    _tokens: List[str]
    metadata: PreppedTokenMetadata

    word_end_token_added: bool
    formatter: Callable[[List[str]], Any]

    starts_with_incomplete_token: bool
    ends_with_incomplete_token: bool
    full_to_sub_token_indices: List[int] = field(compare=False)
    sub_to_full_token_indices: Mapping[int, int] = field(compare=False)

    def __post_init__(self):
        pass

    def _do_token_creation_sanity_check(self):
        if not isinstance(self._tokens, list):
            raise AssertionError()
        n_subtokens_per_token = self.metadata.n_subtokens_per_token
        if len(self._tokens) != sum(n_subtokens_per_token):
            raise ValueError(f"Tokens and metadata are out-of-sync.\n"
                             f"The subword list has {len(self._tokens)} elements but "
                             f"the number of sub-tokens according to metadata is {sum(n_subtokens_per_token)}.")
        if self.word_end_token_added:
            token_seq_full = _SubToFullTokenIterator(self._tokens, self.metadata, formatter=lambda l: "".join(l))
            full_token_without_end_token = None
            for ind, full_token in enumerate(token_seq_full):
                if full_token_without_end_token:
                    raise AssertionError(f'Token {full_token_without_end_token} according to metadata is end-token, however it doesn\'t contain </t>.')
                if not is_terminal_subtoken(full_token):
                    full_token_without_end_token = full_token
                    if not self.ends_with_incomplete_token:
                        raise AssertionError(f'Token {full_token} according to metadata is end-token, however it doesn\'t contain </t>.')

    @staticmethod
    def _build_indexes(metadata: PreppedTokenMetadata) -> Tuple[List[int], Mapping[int, int]]:
        full_to_sub_token_indices = [0] + list(cum_sum(metadata.n_subtokens_per_token))
        sub_to_full_token_indices = {n: i for i, n in enumerate(full_to_sub_token_indices)}
        return full_to_sub_token_indices, sub_to_full_token_indices

    @staticmethod
    def create(tokens: List[str] = None, metadata: PreppedTokenMetadata = None,
               full_token_view: bool = True,
               word_end_token_added: bool = True,
               formatter=lambda x:x,
               starts_with_incomplete_token: bool = False,
               ends_with_incomplete_token: bool = False) -> 'TokenSequence':
        tokens = tokens or []
        metadata = metadata if metadata is not None else PreppedTokenMetadata()
        sequence_type = FullTokenSequence if full_token_view else SubTokenSequence

        # TODO add optimization for [:n] slicing (not rebuilding indices fully)
        full_to_sub_token_indices, sub_to_full_token_indices = TokenSequence._build_indexes(metadata)

        return sequence_type(tokens, metadata, word_end_token_added=word_end_token_added,
                                          formatter=formatter,
                                          starts_with_incomplete_token=starts_with_incomplete_token,
                                          ends_with_incomplete_token=ends_with_incomplete_token,
                             full_to_sub_token_indices=full_to_sub_token_indices,
                             sub_to_full_token_indices=sub_to_full_token_indices)

    @staticmethod
    def as_sequence(token_seq: 'TokenSequence', **kwargs) -> 'TokenSequence':
        return token_seq.shallow_copy(type(token_seq), **kwargs)

    @staticmethod
    def empty(full_token_view: bool = True) -> 'TokenSequence':
        return TokenSequence.create(full_token_view=True) if full_token_view else TokenSequence.create(full_token_view=False)

    def is_complete(self) -> bool:
        return not self.starts_with_incomplete_token and not self.ends_with_incomplete_token

    def shallow_copy(self, new_type, **kwargs) -> 'TokenSequence':
        dict_copy = {k:v for k, v in self.__dict__.items() if k in self.__dataclass_fields__}
        dict_copy.update(kwargs)
        return new_type(**dict_copy)

    @staticmethod
    def _check_concatenation_possible(current: 'TokenSequence', other: 'TokenSequence') -> None:
        if not isinstance(other, TokenSequence):
            raise TypeError(f'Cannot add {type(other)} to a {type(current)}.')
        if current.ends_with_incomplete_token != other.starts_with_incomplete_token:
            raise ValueError(f"Cannot concat these sequences: ...{current[-1:]} and {other[:0]}...")
        elif current.ends_with_incomplete_token and current.metadata.token_types[-1] != other.metadata.token_types[0]:
            raise ValueError(f"Cannot glue subtokens of different types: ...{current[-1:]} and {other[:0]}...")

    #TODO TokenSequenceBuilder class? and when building do the sanity check
    def extend(self, other: 'TokenSequence') -> 'TokenSequence':
        """
        >>> from codeprep.api.text import bpe
        >>> token_seq = bpe('is locked', '10k').with_format(lambda s: "".join(s))

        >>> token_seq.extend(TokenSequence.empty())
        ['is</t>', 'locked</t>']
        >>> token_seq.extend(token_seq)
        ['is</t>', 'locked</t>', 'is</t>', 'locked</t>']
        >>> token_seq.extend(token_seq.subtokens)
        ['is</t>', 'locked</t>', 'is</t>', 'locked</t>', 'is</t>', 'locked</t>', 'is</t>', 'locked</t>']
        """
        self._check_concatenation_possible(self, other)

        first_sub_token_len = len(self.subtokens)
        first_full_token_len = len(self.fulltokens)
        second_full_token_len = len(other.fulltokens)

        self._tokens.extend(other._tokens)
        other_metadata = other.metadata
        start_from = 0
        if self.ends_with_incomplete_token:
            n_subtokens_in_merged_tokens = self.metadata.n_subtokens_per_token[-1] + other_metadata.n_subtokens_per_token[0]
            incomplete_chunk_between = PreppedTokenMetadata([n_subtokens_in_merged_tokens], [self.metadata.token_types[-1]])
            self.metadata.pop()
            self.metadata.update_(incomplete_chunk_between)
            other_metadata = other_metadata[1:]
            to_del = self.full_to_sub_token_indices[-1]
            self.full_to_sub_token_indices[-1] += other.metadata.n_subtokens_per_token[0]
            del(self.sub_to_full_token_indices[to_del])
            self.sub_to_full_token_indices[self.full_to_sub_token_indices[-1]] = len(self.full_to_sub_token_indices) - 1
            start_from += 1

        self.metadata.update_(other_metadata)

        for full_word_index_in_second in range(start_from, second_full_token_len):
            end_of_i_full_word_in_second = other.full_to_sub_token_indices[full_word_index_in_second + 1] + first_sub_token_len
            self.full_to_sub_token_indices.append(end_of_i_full_word_in_second)
            self.sub_to_full_token_indices[end_of_i_full_word_in_second] = full_word_index_in_second + 1 + first_full_token_len - start_from

        assert len(self.fulltokens) + 1 == len(self.sub_to_full_token_indices)
        assert len(self.fulltokens) + 1 == len(self.full_to_sub_token_indices)

        self.word_end_token_added = self.word_end_token_added and other.word_end_token_added
        self.ends_with_incomplete_token = other.ends_with_incomplete_token

        return self

    def __add__(self, other: 'TokenSequence') -> 'TokenSequence':
        self._check_concatenation_possible(self, other)

        resulting_tokens = self._tokens + other._tokens
        if not self.ends_with_incomplete_token:
            resulting_metadata = self.metadata + other.metadata
        elif self.ends_with_incomplete_token:
            n_subtokens_in_merged_tokens = self.metadata.n_subtokens_per_token[-1] + other.metadata.n_subtokens_per_token[0]
            incomplete_chunk_between = PreppedTokenMetadata([n_subtokens_in_merged_tokens], [self.metadata.token_types[-1]])
            resulting_metadata = self.metadata[:-1] + incomplete_chunk_between + other.metadata[1:]

        # TODO do not use create! index doesn't need to be rebuilt from scratch! use extend method?
        return TokenSequence.create(resulting_tokens, resulting_metadata,
                                    full_token_view=not isinstance(self, SubTokenSequence),
                                    word_end_token_added=self.word_end_token_added and other.word_end_token_added,
                                    formatter=self.formatter,
                                    starts_with_incomplete_token=self.starts_with_incomplete_token,
                                    ends_with_incomplete_token=other.ends_with_incomplete_token)

    @abstractmethod
    def single_token(self, include_debug_tokens: bool = False, keep_word_end_token: bool = True) -> str:
        pass

    @abstractmethod
    def __iter__(self) -> Union[Iterator[str], Iterator['TokenSequence']]:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    def __repr__(self):
        #TODO return also object type name
        return repr([i for i in iter(self)])

    def __str__(self):
        return repr([i for i in iter(self)])

    @property
    def fulltokens(self) -> 'TokenSequence':
        if type(self) == FullTokenSequence:
            return self
        return self.shallow_copy(FullTokenSequence)
    
    @property
    def subtokens(self):
        if type(self) == SubTokenSequence:
            return self
        return self.shallow_copy(SubTokenSequence)

    @abstractmethod
    def aligned_iterator(self, over, over_full_tokens: bool, formatter: Callable[[List[str]], Any]) -> Iterator:
        """
        >>> from codeprep.api.text import bpe
        >>> token_seq = bpe('is locked', '10k')
        >>> token_seq
        [['is</t>'], ['loc', 'ked</t>']]

        >>> iterator = token_seq.subtokens.aligned_iterator([1, 2], over_full_tokens=True)
        >>> [x for x in iterator]
        [1, 2, 2]
        >>> iterator = token_seq.subtokens.aligned_iterator([1, 2, 3], over_full_tokens=False)
        >>> [x for x in iterator]
        [1, 2, 3]
        >>> iterator = token_seq.fulltokens.aligned_iterator([1, 2], over_full_tokens=True)
        >>> [x for x in iterator]
        [1, 2]
        >>> iterator = token_seq.fulltokens.aligned_iterator([1, 2, 3], over_full_tokens=False)
        >>> [x for x in iterator]
        [[1], [2, 3]]
        """
        pass

    def with_format(self, formatter: Callable[[List[str]], Any]) -> 'TokenSequence':
        """
        >>> from codeprep.api.text import bpe
        >>> token_seq = bpe('is locked', '10k')
        >>> token_seq
        [['is</t>'], ['loc', 'ked</t>']]

        >>> token_seq.subtokens.with_format(lambda s: "".join(s))
        ['is</t>', 'locked</t>']
        """
        return self.shallow_copy(FullTokenSequence, formatter=formatter)

    @abstractmethod
    def __getitem__(self, item: Union[int, slice]) -> 'TokenSequence':
        pass

    @staticmethod
    def _normalize_index(index: Optional[int], is_slice: bool, total: int) -> Optional[int]:
        """
        >>> TokenSequence._normalize_index(None, is_slice=False, total=2) is None
        True
        >>> TokenSequence._normalize_index(-3, is_slice=False, total=2)
        Traceback (most recent call last):
        ...
        KeyError: -3
        >>> TokenSequence._normalize_index(-2, is_slice=False, total=2)
        0
        >>> TokenSequence._normalize_index(-1, is_slice=False, total=2)
        1
        >>> TokenSequence._normalize_index(0, is_slice=False, total=2)
        0
        >>> TokenSequence._normalize_index(1, is_slice=False, total=2)
        1
        >>> TokenSequence._normalize_index(2, is_slice=False, total=2)
        2
        >>> TokenSequence._normalize_index(3, is_slice=False, total=2)
        2
        >>> TokenSequence._normalize_index(1000, is_slice=False, total=2)
        2

        >>> TokenSequence._normalize_index(None, is_slice=True, total=2) is None
        True
        >>> TokenSequence._normalize_index(-3, is_slice=True, total=2)
        0
        >>> TokenSequence._normalize_index(-2, is_slice=True, total=2)
        0
        >>> TokenSequence._normalize_index(-1, is_slice=True, total=2)
        1
        >>> TokenSequence._normalize_index(0, is_slice=True, total=2)
        0
        >>> TokenSequence._normalize_index(1, is_slice=True, total=2)
        1
        >>> TokenSequence._normalize_index(2, is_slice=True, total=2)
        2
        >>> TokenSequence._normalize_index(3, is_slice=True, total=2)
        2
        >>> TokenSequence._normalize_index(1000, is_slice=True, total=2)
        2
        """
        if index is None:
            return None

        if index > total:
            return total

        if index >= 0:
            norm_index = index
        else:
            norm_index = total + index

            if norm_index < 0:
                if is_slice:
                    return 0
                else:
                    raise KeyError(index)

        return norm_index

    def _full_to_sub_index(self, index: Optional[int]) -> Optional[int]:
        if index is None:
            return index
        return self.full_to_sub_token_indices[index]

    def _sub_to_full_index(self, index: Optional[int]) -> Optional[int]:
        if index is None:
            return index
        try:
            return self.sub_to_full_token_indices[index]
        except KeyError:
            raise KeyError(f"Sub-index {index} is in the middle of a full-tokens")

    def _sub_to_adjusted_full_index(self, index: int, to_left: bool):
        if index is None:
            return None

        while index not in self.sub_to_full_token_indices:
            if to_left:
                index -= 1
            else:
                index += 1
        return self.sub_to_full_token_indices[index]

    @staticmethod
    def _normalize_index_or_slice(item: Union[int, slice], total: int) -> Tuple[int, int]:
        if isinstance(item, int):
            start = TokenSequence._normalize_index(item, is_slice=False, total=total)
            stop = start + 1 if start < total else start
        elif isinstance(item, slice):
            if item.step is not None:
                raise NotImplemented("It is not possible to specify step")

            start = TokenSequence._normalize_index(item.start, is_slice=True, total=total)
            stop = TokenSequence._normalize_index(item.stop, is_slice=True, total=total)
        else:
            raise TypeError()

        return start, stop


@dataclass(repr=False)
class SubTokenSequence(TokenSequence):
    def __iter__(self) -> Union[Iterator[str], Iterator[TokenSequence]]:
        return self.iter()

    def iter(self, metadata: bool = False) -> Union[Iterator[str], Iterator[TokenSequence]]:
        if metadata:
            return iter([self[i] for i in range(len(self))])
        else:
            return iter(self._tokens)

    def __getitem__(self, item: Union[int, slice]):
        start, stop = TokenSequence._normalize_index_or_slice(item, total=len(self))

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
        ends_with_incomplete_token = (adjusted_after > 0) or ((stop == len(self._tokens) or stop is None) and self.ends_with_incomplete_token)

        full_to_sub_token_indices, sub_to_full_token_indices = self._build_indexes(metadata)

        return self.shallow_copy(new_type=type(self), _tokens=self._tokens[start:stop], metadata=metadata,
                                 starts_with_incomplete_token=starts_with_incomplete_token,
                                 ends_with_incomplete_token=ends_with_incomplete_token,
                                 full_to_sub_token_indices=full_to_sub_token_indices,
                                 sub_to_full_token_indices=sub_to_full_token_indices)

    def __len__(self) -> int:
        return len(self._tokens)

    def aligned_iterator(self, over, over_full_tokens: bool, formatter: Callable[[List[str]], Any] = lambda x: x) -> Iterator:
        return _FullToSubTokenIterator(over, self.metadata) if over_full_tokens else iter(over)

    def single_token(self, include_debug_tokens: bool = False, keep_word_end_token: bool = True) -> str:
        """
        >>> from codeprep.api.text import bpe
        >>> token_seq = bpe('is locked', '10k')
        >>> token_seq
        [['is</t>'], ['loc', 'ked</t>']]
        >>> token_seq.subtokens[0].single_token()
        'is</t>'
        >>> token_seq.subtokens[1].single_token()
        'loc'
        >>> token_seq.subtokens[0:2].single_token()
        Traceback (most recent call last):
        ...
        ValueError: This method can be only called if the sequence contains only one token.
        """
        if len(self) != 1:
            raise ValueError("This method can be only called if the sequence contains only one token.")

        return self._tokens[0]

@dataclass(repr=False)
class FullTokenSequence(TokenSequence):
    def __iter__(self) -> Union[Iterator[str], Iterator['TokenSequence']]:
        return self.iter()

    def iter(self, metadata: bool = False) -> Union[Iterator[str], Iterator['TokenSequence']]:
        over = self.subtokens if metadata else self._tokens
        formatter = (lambda x: x) if metadata else self.formatter
        return _SubToFullTokenIterator(over, metadata=self.metadata, formatter=formatter)

    def aligned_iterator(self, over: Sequence[Any], over_full_tokens: bool, formatter: Callable[[List[str]], Any] = lambda x: x) -> Iterator:
        return iter(over) if over_full_tokens else _SubToFullTokenIterator(over, metadata=self.metadata, formatter=formatter)

    def __setitem__(self, key, value):
        if not isinstance(value, FullTokenSequence):
            raise TypeError("Can assign only TokenSequence instance")

        self.__dict__ = self[:key].extend(value).extend(self[key + 1:]).__dict__

    def __getitem__(self, item: Union[int, slice]):
        start, stop = TokenSequence._normalize_index_or_slice(item, total=len(self))

        full_item = slice(
            self._full_to_sub_index(start),
            self._full_to_sub_index(stop),
            1,
        )

        metadata=PreppedTokenMetadata(
            self.metadata.n_subtokens_per_token[start:stop],
            self.metadata.token_types[start:stop]
        )

        starts_with_incomplete_token = self.starts_with_incomplete_token and (start==0 or start is None)
        ends_with_incomplete_token = self.ends_with_incomplete_token and (stop==len(self) or stop is None)

        full_to_sub_token_indices, sub_to_full_token_indices = self._build_indexes(metadata)

        return self.shallow_copy(new_type=type(self), _tokens=self._tokens[full_item],
                                 metadata=metadata, starts_with_incomplete_token=starts_with_incomplete_token,
                                 ends_with_incomplete_token=ends_with_incomplete_token,
                                 full_to_sub_token_indices=full_to_sub_token_indices,
                                 sub_to_full_token_indices=sub_to_full_token_indices)

    def __len__(self):
        return self.sub_to_full_token_indices[len(self._tokens)]

    def single_token(self, include_debug_tokens: bool = False, keep_word_end_token: bool = True) -> str:
        """
        >>> from codeprep.api.text import bpe
        >>> token = bpe('revolver', '10k')
        >>> token
        [['re', 'v', 'ol', 'ver</t>']]
        >>> token.single_token()
        'revolver</t>'
        >>> token.single_token(include_debug_tokens=True)
        're|v|ol|ver</t>'

        >>> token.single_token(keep_word_end_token=False)
        'revolver'

        >>> multiple_tokens = bpe('// hj', '10k')
        >>> multiple_tokens.single_token()
        Traceback (most recent call last):
        ...
        ValueError: This method can be only called if the sequence contains only one token.

        >>> special_token = multiple_tokens.fulltokens[-1]
        >>> special_token
        [['<EOL></t>']]
        >>> special_token.single_token()
        '<EOL></t>'
        """
        if len(self) != 1:
            raise ValueError("This method can be only called if the sequence contains only one token.")

        separator = '|' if include_debug_tokens else ''
        full_token = separator.join(self._tokens)

        if not is_terminal_subtoken(full_token):
            raise ValueError(f'{full_token} is not a full token')

        full_token = full_token if keep_word_end_token else full_token[:-len(placeholders['compound_word_end'])]
        return full_token


def is_terminal_subtoken(subtoken: str, use_token_end_chars: bool = True) -> bool:
    if not use_token_end_chars:
        raise NotImplemented("Finding out if a subtoken is terminal for tokens represented with <w> and </w> tokens "
                             "is not yet implemented.")

    return subtoken.endswith(placeholders['compound_word_end']) or subtoken == '`pad'