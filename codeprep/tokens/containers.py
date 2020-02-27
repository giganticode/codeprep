# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import List, Union, Optional

from codeprep.noneng import replace_non_ascii_seqs
from codeprep.preprocess.core import ReprConfig, torepr
from codeprep.preprocess.result import PreprocessingResult
from codeprep.preprocess.metadata import PreppedTokenMetadata
from codeprep.preprocess.placeholders import placeholders
from codeprep.tokens.rootclasses import ParsedToken, ParsedSubtoken
from codeprep.tokens.whitespace import SpaceInString
from codeprep.tokens.word import Word


class ProcessableTokenContainer(ParsedToken):
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
        return " ".join(self.non_preprocessed_repr().tokens)


def wrap_in_word_boundaries_if_necessary(res: List[str]) -> List[str]:
    if len(res) == 1 or (len(res) == 2 and res[0] in [placeholders['capitals'], placeholders['capital']]):
        return res
    else:
        return [placeholders['word_start']] + res + [placeholders['word_end']]


class SplitContainer(ProcessableTokenContainer):
    def __init__(self, subtokens: List[ParsedSubtoken]):
        super().__init__(subtokens)

    def empty_repr(self):
        return self.subtokens

    def __repr__(self):
        return f'{self.__class__.__name__}{self.subtokens}'

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> PreprocessingResult:
        nospl_str = ["".join(map(lambda s: torepr(s, repr_config).tokens[0], self.subtokens))]
        return self.wrap_in_metadata_for_full_word(nospl_str)

    def preprocessed_repr(self, repr_config) -> PreprocessingResult:
        if repr_config.bpe_data:
            return self.wrap_in_metadata_for_full_word(repr_config.word_splitter(str(self), repr_config.bpe_data))
        total_preprocessing_result = PreprocessingResult()
        for subtoken in self.subtokens:
            preprocessing_result = torepr(subtoken, repr_config)
            total_preprocessing_result.update_(preprocessing_result)
        return self.wrap_in_metadata_for_full_word(wrap_in_word_boundaries_if_necessary(total_preprocessing_result.tokens), total_preprocessing_result.non_processable_tokens)

    @classmethod
    def from_single_token(cls, token: str):
        return cls([Word.from_(token)])


class TextContainer(ProcessableTokenContainer):

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


class Comment(TextContainer):
    def __init__(self, tokens: List[ParsedToken]):
        super().__init__(tokens)

    def preprocessed_repr(self, repr_config: ReprConfig) -> PreprocessingResult:
        return self.wrap_in_metadata_for_full_word([placeholders['comment']])


class OneLineComment(Comment):
    def __init__(self, tokens: List[ParsedToken]):
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> PreprocessingResult:
        preprocessing_result = torepr(self.subtokens, repr_config)
        preprocessing_result.metadata.update(PreppedTokenMetadata(word_boundaries=[0, 1], token_types=[OneLineComment]))
        preprocessing_result.metadata.set_all_tokens_type(OneLineComment)
        preprocessing_result.tokens.append(placeholders['olc_end'])
        return preprocessing_result


class MultilineComment(Comment):
    def __init__(self, tokens: List[ParsedToken]):
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> PreprocessingResult:
        preprocessing_result = torepr(self.subtokens, repr_config)
        preprocessing_result.metadata.set_all_tokens_type(MultilineComment)
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
        if not repr_config: #called by str()
            return self.wrap_in_metadata_for_full_word(["".join(map(lambda t: str(t), self.subtokens))])
        elif self.length > repr_config.max_str_length:
            s = ['""'] if repr_config.full_strings else ['"', '"']
            non_processable_tokens = {} if repr_config.full_strings else {'"'}
            return self.wrap_in_metadata_for_full_word(s, non_processable_tokens)
        elif repr_config.bpe_data:
            s = self._replace_non_ascii_seqs_if_necessary(repr_config)
            return self.wrap_in_metadata_for_full_word(repr_config.word_splitter(s, repr_config.bpe_data))
        elif repr_config.full_strings:
            s = self._replace_non_ascii_seqs_if_necessary(repr_config)
            return self.wrap_in_metadata_for_full_word([s])
        else: # here we dont keep full strings
            preprocessing_result = torepr(list(filter(lambda t: type(t) != SpaceInString, self.subtokens)), repr_config)
            preprocessing_result.metadata.set_all_tokens_type(StringLiteral)
            return preprocessing_result

    def preprocessed_repr(self, repr_config: ReprConfig) -> PreprocessingResult:
        return self.wrap_in_metadata_for_full_word([placeholders['string_literal']])

    def __eq__(self, other):
        return super().__eq__(other) and self.length == other.length

    def _repr__(self):
        return super().__repr__() + f" , length: {self.length}"
