# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0
from abc import ABC
from typing import List, Union, Optional, Type

from codeprep.noneng import replace_non_ascii_seqs
from codeprep.preprocess.codestructure import PureSnippetStructure
from codeprep.preprocess.core import ReprConfig, torepr
from codeprep.preprocess.result import PreprocessingResult
from codeprep.preprocess.tokens import TokenSequence
from codeprep.preprocess.metadata import PreppedTokenMetadata
from codeprep.preprocess.placeholders import placeholders
from codeprep.tokentypes.rootclasses import ParsedToken, ParsedSubtoken
from codeprep.tokentypes.whitespace import SpaceInString, NewLine
from codeprep.tokentypes.word import Word


def set_all_tokens_type(token_seq: TokenSequence, t: Type) -> TokenSequence:
    metadata = token_seq.metadata
    metadata.token_types = [t] * len(metadata.n_subtokens_per_token)
    return TokenSequence.as_sequence(token_seq, metadata=metadata)


class ProcessableTokenContainer(ParsedToken, ABC):
    def __init__(self, subtokens: Union[List[ParsedSubtoken], List[ParsedToken]]):
        if isinstance(subtokens, list):
            self.subtokens = subtokens
        else:
            raise AssertionError(f"Should be list but is: {subtokens}")

    def add(self, token):
        self.subtokens.append(token)

    def get_subtokens(self):
        return self.subtokens

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.subtokens == other.subtokens

    def __repr__(self):
        return f'{self.__class__.__name__}{self.subtokens}'

    def __str__(self):
        return " ".join(self.non_preprocessed_repr().prepped_tokens._tokens)

    def get_n_additional_empty_lines(self) -> int:
        return sum([isinstance(subtoken, NewLine) for subtoken in self.subtokens])


def wrap_in_word_boundaries_if_necessary(res: List[str]) -> List[str]:
    if len(res) == 1 or (len(res) == 2 and res[0] in [placeholders['capitals'], placeholders['capital']]):
        return res
    else:
        return [placeholders['word_start']] + res + [placeholders['word_end']]


class Identifier(ProcessableTokenContainer):
    def __init__(self, subtokens: List[ParsedSubtoken]):
        super().__init__(subtokens)

    def empty_repr(self):
        return self.subtokens

    def __repr__(self):
        return f'{self.__class__.__name__}{self.subtokens}'

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> PreprocessingResult:
        nospl_str = ["".join(map(lambda s: torepr(s, repr_config), self.subtokens))]
        return self._wrap_in_metadata_for_full_word(nospl_str, self.get_n_additional_empty_lines())

    def preprocessed_repr(self, repr_config) -> PreprocessingResult:
        if repr_config.bpe_data:
            return self._wrap_in_metadata_for_full_word(repr_config.word_splitter(str(self), repr_config.bpe_data), self.get_n_additional_empty_lines())
        total_preprocessing_result = []
        for subtoken in self.subtokens:
            total_preprocessing_result += torepr(subtoken, repr_config)
        return self._wrap_in_metadata_for_full_word(wrap_in_word_boundaries_if_necessary(total_preprocessing_result),
                                                    self.get_n_additional_empty_lines(), set())

    @classmethod
    def from_single_token(cls, token: str):
        return cls([Word.from_(token)])


class TextContainer(ProcessableTokenContainer, ABC):

    def __init__(self, tokens: List[ParsedToken]):
        super().__init__(tokens)
        for token in tokens:
            if isinstance(token, ParsedSubtoken):
                raise TypeError(
                    f"ParsedTokens cannot be a part of Text container, but one ofn the tokens passed was {type(token)} ({token})")

    def __repr__(self):
        return f'{self.__class__.__name__}{self.subtokens}'

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.subtokens == other.subtokens


class Comment(TextContainer, ABC):
    def __init__(self, tokens: List[ParsedToken]):
        super().__init__(tokens)

    def preprocessed_repr(self, repr_config: ReprConfig) -> PreprocessingResult:
        return self._wrap_in_metadata_for_full_word([placeholders['comment']], self.get_n_additional_empty_lines())


class OneLineComment(Comment):
    def __init__(self, tokens: List[ParsedToken]):
        super().__init__(tokens)

    @staticmethod
    def is_possible_code_structure(per_line_subtokens_numbers: List[int]):
        return (len(per_line_subtokens_numbers) == 2 and per_line_subtokens_numbers[1] == 0) or len(per_line_subtokens_numbers) == 1

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> PreprocessingResult:
        preprocessing_result = torepr(self.subtokens, repr_config)
        n_sub_tokens_per_token = preprocessing_result.prepped_tokens.metadata.n_subtokens_per_token + [1]
        per_line_subtokens_numbers = preprocessing_result.code_snippet_structure.subtokens_in_each_line
        if not OneLineComment.is_possible_code_structure(per_line_subtokens_numbers):
            raise AssertionError()
        preprocessing_result.prepped_tokens = TokenSequence.create(
            preprocessing_result.prepped_tokens._tokens + [placeholders['olc_end']],
            PreppedTokenMetadata(
                n_sub_tokens_per_token,
                [OneLineComment] * len(n_sub_tokens_per_token)
            ),
            word_end_token_added=False
        )
        n_additional_empty_lines = self.get_n_additional_empty_lines()
        assert n_additional_empty_lines <= 1
        preprocessing_result.code_snippet_structure = PureSnippetStructure.of([per_line_subtokens_numbers[0] + 1] + [0] * n_additional_empty_lines)
        return preprocessing_result


class MultilineComment(Comment):
    def __init__(self, tokens: List[ParsedToken]):
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> PreprocessingResult:
        preprocessing_result = torepr(self.subtokens, repr_config)
        preprocessing_result.prepped_tokens = set_all_tokens_type(preprocessing_result.prepped_tokens, MultilineComment)
        return preprocessing_result


class StringLiteral(TextContainer):
    def __init__(self, tokens: List[ParsedToken], length: int):
        super().__init__(tokens)
        self.length = length

    def _replace_non_ascii_seqs_if_necessary(self,repr_config: ReprConfig) -> str:
        s = str(self)
        if 'NonEng' in list(map(lambda x: x.__name__, repr_config.types_to_be_repr)):
            s = placeholders["space_in_str"].join(map(lambda t: replace_non_ascii_seqs(t, placeholders['non_ascii_seq']), s.split(placeholders["space_in_str"])))    
        return s

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> PreprocessingResult:
        n_subtokens_in_each_line = self.get_n_additional_empty_lines()
        if not repr_config: #called by str()
            return self._wrap_in_metadata_for_full_word(["".join(map(lambda t: str(t), self.subtokens))], n_subtokens_in_each_line)
        elif self.length > repr_config.max_str_length:
            return PreprocessingResult(TokenSequence.create([], PreppedTokenMetadata([], [])), {}, PureSnippetStructure.of([0]))
        elif repr_config.bpe_data:
            s = self._replace_non_ascii_seqs_if_necessary(repr_config)
            return self._wrap_in_metadata_for_full_word(repr_config.word_splitter(s, repr_config.bpe_data), n_subtokens_in_each_line)
        elif repr_config.full_strings:
            s = self._replace_non_ascii_seqs_if_necessary(repr_config)
            return self._wrap_in_metadata_for_full_word([s], n_subtokens_in_each_line)
        else: # here we dont keep full strings
            preprocessing_result = torepr(list(filter(lambda t: type(t) != SpaceInString, self.subtokens)), repr_config)
            preprocessing_result.prepped_tokens = set_all_tokens_type(preprocessing_result.prepped_tokens, StringLiteral)
            return preprocessing_result

    def preprocessed_repr(self, repr_config: ReprConfig) -> PreprocessingResult:
        return self._wrap_in_metadata_for_full_word([placeholders['string_literal']], self.get_n_additional_empty_lines())

    def __eq__(self, other):
        return super().__eq__(other) and self.length == other.length

    def _repr__(self):
        return super().__repr__() + f" , length: {self.length}"
