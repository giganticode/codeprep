from typing import List, Tuple, Union, Optional

from dataprep.model.core import ParsedToken, ParsedSubtoken
from dataprep.model.metadata import PreprocessingMetadata
from dataprep.model.placeholders import placeholders
from dataprep.model.word import Word
from dataprep.preprocess.core import ReprConfig, torepr
from dataprep.split.ngram import NgramSplittingType, do_ngram_splitting


class ProcessableTokenContainer(ParsedToken):
    def __init__(self, subtokens):
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


def wrap_in_word_boundaries_if_necessary(res: List[str]) -> List[str]:
    if len(res) == 1 or (len(res) == 2 and res[0] in [placeholders['capitals'], placeholders['capital']]):
        return res
    else:
        return [placeholders['word_start']] + res + [placeholders['word_end']]


class SplitContainer(ProcessableTokenContainer):
    def __init__(self, subtokens):
        super().__init__(subtokens)

    def empty_repr(self):
        return self.subtokens

    def __str__(self):
        return self.non_preprocessed_repr(ReprConfig.empty())[0]

    def __repr__(self):
        return f'{self.__class__.__name__}{self.subtokens}'

    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        # TODO refactor
        nospl_str = "".join(map(lambda s: torepr(s, repr_config)[0][0], self.subtokens))
        if repr_config.ngram_split_config and repr_config.ngram_split_config.splitting_type == NgramSplittingType.RONIN:
            parts = do_ngram_splitting(nospl_str, repr_config.ngram_split_config)
        else:
            parts = [nospl_str]
        return self.with_full_word_metadata(wrap_in_word_boundaries_if_necessary(parts))
        # return "".join(map(lambda s: s.non_preprocessed_repr(repr_config) if isinstance(s, NonEng) else str(s), self.subtokens))

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
    def __str__(self):
        return " ".join([str(s) for s, _ in self.non_preprocessed_repr(ReprConfig.empty())])

    def __init__(self, tokens):
        super().__init__(tokens)
        for token in tokens:
            if isinstance(token, ParsedSubtoken):
                raise TypeError(f"ParsedTokens cannot be a part of Text container, but one ofn the tokens passed was {type(token)} ({token})")

    def __repr__(self):
        return f'{self.__class__.__name__}{self.subtokens}'

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.subtokens == other.subtokens

    def with_each_word_metadata(self, tokens: List[str], metadata: Optional[PreprocessingMetadata] = None) -> Tuple[Union[List[str], str], PreprocessingMetadata]:
        updated_metadata = metadata or PreprocessingMetadata()
        updated_metadata.word_boundaries = list(range(len(tokens)+1))
        return tokens, updated_metadata


class OneLineComment(TextContainer):
    def __init__(self, tokens):
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        prep_tokens, metadata = torepr(self.subtokens, repr_config)
        metadata.update(PreprocessingMetadata(word_boundaries=[0, 1]))
        return prep_tokens + [placeholders['olc_end']], metadata

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return self.with_each_word_metadata([placeholders['comment']])


class MultilineComment(TextContainer):
    def __init__(self, tokens):
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return torepr(self.subtokens, repr_config)

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return self.with_each_word_metadata([placeholders['comment']])


class StringLiteral(TextContainer):
    def __init__(self, tokens):
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return torepr(self.subtokens, repr_config)

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return self.with_each_word_metadata([placeholders['string_literal']])
