from typing import List, Tuple, Union, Optional

from dataprep.model.core import ParsedToken, ParsedSubtoken
from dataprep.model.metadata import PreprocessingMetadata
from dataprep.model.noneng import NonEng, NonEngContent
from dataprep.model.placeholders import placeholders
from dataprep.model.word import Word
from dataprep.preprocess.core import ReprConfig, torepr


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


class SplitContainer(ProcessableTokenContainer):
    def __init__(self, subtokens):
        super().__init__(subtokens)

    def empty_repr(self):
        return self.subtokens

    def __str__(self):
        return self.non_preprocessed_repr(ReprConfig.empty())[0]

    def __repr__(self):
        return f'{self.__class__.__name__}{self.subtokens}'

    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[str, PreprocessingMetadata]:
        # TODO refactor
        return self.with_full_word_metadata("".join(map(lambda s: torepr(s, repr_config)[0][0], self.subtokens)))
        # return "".join(map(lambda s: s.non_preprocessed_repr(repr_config) if isinstance(s, NonEng) else str(s), self.subtokens))

    def preprocessed_repr(self, repr_config) -> Tuple[List[str], PreprocessingMetadata]:
        res = []
        all_metadata = PreprocessingMetadata()
        for subtoken in self.subtokens:
            r, metadata = torepr(subtoken, repr_config)
            res.extend(r if isinstance(r, list) else [r])
            all_metadata.update(metadata)
        if len(res) == 1 or (len(res) == 2 and res[0] in [placeholders['capitals'], placeholders['capital']]):
            return self.with_full_word_metadata(res, all_metadata)
        else:
            return self.with_full_word_metadata([placeholders['word_start']] + res + [placeholders['word_end']], all_metadata)

    @classmethod
    def from_single_token(cls, token: str):
        return cls([Word.from_(token)])


class TextContainer(ProcessableTokenContainer):
    def __str__(self):
        return " ".join([str(s) for s, _ in self.non_preprocessed_repr(ReprConfig.empty())])

    @classmethod
    def __calc_non_eng_percent(cls, tokens):
        total = len(tokens)
        #TODO this is legacy logic, which is not currently used. Strongly consider removing this
        non_eng = sum(map(lambda x: isinstance(x, SplitContainer) and isinstance(x.get_subtokens()[0], NonEng), tokens))
        return float(non_eng) / total if total != 0 else 0.0, non_eng

    def __init__(self, tokens):
        super().__init__(tokens)
        for token in tokens:
            if isinstance(token, ParsedSubtoken):
                raise TypeError(f"ParsedTokens cannot be a part of Text container, but one ofn the tokens passed was {type(token)} ({token})")

        self.non_eng_percent, self.non_eng_qty = self.__calc_non_eng_percent(tokens)

    def __repr__(self):
        return f'{self.__class__.__name__}{self.subtokens} %={self.non_eng_percent} N={self.non_eng_qty}'

    def has_non_eng_content(self):
        return self.non_eng_percent > 0.2 and self.non_eng_qty >= 4

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.subtokens == other.subtokens and self.non_eng_percent == other.non_eng_percent and \
               self.non_eng_qty == other.non_eng_qty

    def with_each_word_metadata(self, tokens: List[str], metadata: Optional[PreprocessingMetadata] = None) -> Tuple[Union[List[str], str], PreprocessingMetadata]:
        updated_metadata = metadata or PreprocessingMetadata()
        updated_metadata.word_boundaries = list(range(len(tokens)+1))
        return tokens, updated_metadata


class OneLineComment(TextContainer):
    def __init__(self, tokens):
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        if NonEngContent in repr_config.types_to_be_repr and self.has_non_eng_content():
            return self.with_each_word_metadata(["//", placeholders['non_eng_content'], placeholders['olc_end']])
        else:
            prep_tokens, metadata = torepr(self.subtokens, repr_config)
            metadata.update(PreprocessingMetadata(word_boundaries=[0,1]))
            return prep_tokens + [placeholders['olc_end']], metadata

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return self.with_each_word_metadata([placeholders['comment']])


class MultilineComment(TextContainer):
    def __init__(self, tokens):
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        if NonEngContent in repr_config.types_to_be_repr and self.has_non_eng_content():
            return self.with_each_word_metadata(["/*", placeholders['non_eng_content'], "*/"])
        else:
            return torepr(self.subtokens, repr_config)

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return self.with_each_word_metadata([placeholders['comment']])


class StringLiteral(TextContainer):
    def __init__(self, tokens):
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        if NonEngContent in repr_config.types_to_be_repr and self.has_non_eng_content():
            return self.with_each_word_metadata(["\"", placeholders['non_eng_content'], "\""])
        else:
            return torepr(self.subtokens, repr_config)

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return self.with_each_word_metadata([placeholders['string_literal']])
