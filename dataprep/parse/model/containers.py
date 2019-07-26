from typing import List, Tuple, Union, Optional

from dataprep.parse.model.core import ParsedToken, ParsedSubtoken
from dataprep.parse.model.metadata import PreprocessingMetadata
from dataprep.parse.model.placeholders import placeholders
from dataprep.parse.model.whitespace import SpaceInString
from dataprep.parse.model.word import Word
from dataprep.preprocess.core import ReprConfig, torepr


class ProcessableTokenContainer(ParsedToken):
    def __init__(self, subtokens: Union[List[ParsedSubtoken], List[Union[str, ParsedToken]]]):
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
        return " ".join(self.non_preprocessed_repr()[0])


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

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
        nospl_str = ["".join(map(lambda s: torepr(s, repr_config)[0][0], self.subtokens))]
        return self.with_full_word_metadata(nospl_str)

    def preprocessed_repr(self, repr_config) -> Tuple[List[str], PreprocessingMetadata]:
        res = []
        all_metadata = PreprocessingMetadata()
        for subtoken in self.subtokens:
            r, metadata = torepr(subtoken, repr_config)
            res.extend(r if isinstance(r, list) else [r])
            all_metadata.update(metadata)
        return self.with_full_word_metadata(wrap_in_word_boundaries_if_necessary(res), all_metadata)

    @classmethod
    def from_single_token(cls, token: str):
        return cls([Word.from_(token)])


class TextContainer(ProcessableTokenContainer):

    def __init__(self, tokens: List[Union[str, ParsedToken]]):
        super().__init__(tokens)
        for token in tokens:
            if isinstance(token, ParsedSubtoken):
                raise TypeError(
                    f"ParsedTokens cannot be a part of Text container, but one ofn the tokens passed was {type(token)} ({token})")

    def __repr__(self):
        return f'{self.__class__.__name__}{self.subtokens}'

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.subtokens == other.subtokens

    def with_each_word_metadata(self, tokens: List[str], metadata: Optional[PreprocessingMetadata] = None) -> Tuple[
        Union[List[str], str], PreprocessingMetadata]:
        updated_metadata = metadata or PreprocessingMetadata()
        updated_metadata.word_boundaries = list(range(len(tokens) + 1))
        return tokens, updated_metadata


class OneLineComment(TextContainer):
    def __init__(self, tokens: List[Union[str, ParsedToken]]):
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
        prep_tokens, metadata = torepr(self.subtokens, repr_config)
        metadata.update(PreprocessingMetadata(word_boundaries=[0, 1]))
        return prep_tokens + [placeholders['olc_end']], metadata

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return self.with_each_word_metadata([placeholders['comment']])


class MultilineComment(TextContainer):
    def __init__(self, tokens: List[Union[str, ParsedToken]]):
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
        return torepr(self.subtokens, repr_config)

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return self.with_each_word_metadata([placeholders['comment']])


class StringLiteral(TextContainer):
    def __init__(self, tokens: List[Union[str, ParsedToken]], length: int):
        super().__init__(tokens)
        self.length = length

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
        if repr_config and self.length > repr_config.max_str_length:
            return self.with_each_word_metadata(['""'] if repr_config.full_strings else ['"', '"'],
                                                metadata=PreprocessingMetadata(nonprocessable_tokens={'"'}))
        elif not repr_config or repr_config.full_strings:
            return self.with_each_word_metadata(["".join(map(lambda t: str(t), self.subtokens))])
        else:
            return torepr(list(filter(lambda t: type(t) != SpaceInString, self.subtokens)), repr_config)

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return self.with_each_word_metadata([placeholders['string_literal']])

    def __eq__(self, other):
        return super().__eq__(other) and self.length == other.length

    def _repr__(self):
        return super().__repr__() + f" , length: {self.length}"
