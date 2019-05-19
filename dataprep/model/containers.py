from typing import List

from dataprep.model.chars import Quote, MultilineCommentStart, MultilineCommentEnd, OneLineCommentStart
from dataprep.model.core import ParsedToken
from dataprep.model.noneng import NonEng, NonEngContent
from dataprep.model.placeholders import placeholders
from dataprep.model.word import Word
from dataprep.preprocessors.repr import torepr, ReprConfig


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
        return self.non_preprocessed_repr(ReprConfig.empty())

    def __repr__(self):
        return f'{self.__class__.__name__}{self.subtokens}'

    def non_preprocessed_repr(self, repr_config):
        # TODO refactor
        return "".join(map(lambda s: torepr(s, repr_config)[0], self.subtokens))
        # return "".join(map(lambda s: s.non_preprocessed_repr(repr_config) if isinstance(s, NonEng) else str(s), self.subtokens))

    def preprocessed_repr(self, repr_config) -> List[str]:
        res = []
        for subtoken in self.subtokens:
            r = torepr(subtoken, repr_config)
            res.extend(r if isinstance(r, list) else [r])
        if len(res) == 1 or (len(res) == 2 and res[0] in [placeholders['capitals'], placeholders['capital']]):
            return res
        else:
            return [placeholders['word_start']] + res + [placeholders['word_end']]

    @classmethod
    def from_single_token(cls, token: str):
        return cls([Word.from_(token)])


class TextContainer(ProcessableTokenContainer):
    def __str__(self):
        return " ".join([str(s) for s in self.non_preprocessed_repr(ReprConfig.empty())])

    @classmethod
    def __calc_non_eng_percent(cls, tokens):
        total = len(tokens)
        non_eng = sum(map(lambda x: isinstance(x, NonEng), tokens))
        return float(non_eng) / total if total != 0 else 0.0, non_eng

    def __init__(self, tokens):
        super().__init__(tokens)
        self.non_eng_percent, self.non_eng_qty = self.__calc_non_eng_percent(tokens)

    def __repr__(self):
        return f'{self.__class__.__name__}{self.subtokens} %={self.non_eng_percent} N={self.non_eng_qty}'

    def has_non_eng_content(self):
        return self.non_eng_percent > 0.2 and self.non_eng_qty >= 4

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.subtokens == other.subtokens and self.non_eng_percent == other.non_eng_percent and \
               self.non_eng_qty == other.non_eng_qty


class OneLineComment(TextContainer):
    def __init__(self, tokens):
        if tokens[0] != OneLineCommentStart():
            raise ValueError("The first token must be one-line-comment start token!")
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config):
        if NonEngContent in repr_config.types_to_be_repr and self.has_non_eng_content():
            return ["//", placeholders['non_eng_content'], placeholders['olc_end']]
        else:
            return torepr(self.subtokens, repr_config) + [placeholders['olc_end']]

    def preprocessed_repr(self, repr_config) -> List[str]:
        return [placeholders['comment']]


class MultilineComment(TextContainer):
    def __init__(self, tokens):
        if tokens[0] != MultilineCommentStart() or tokens[-1] != MultilineCommentEnd():
            raise ValueError("The first and the last tokens must be multiline-comment start and end tokens!")
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config):
        if NonEngContent in repr_config.types_to_be_repr and self.has_non_eng_content():
            return ["/*", placeholders['non_eng_content'], "*/"]
        else:
            return torepr(self.subtokens, repr_config)

    def preprocessed_repr(self, repr_config) -> List[str]:
        return [placeholders['comment']]


class StringLiteral(TextContainer):
    def __init__(self, tokens):
        if tokens[0] != Quote() or tokens[-1] != Quote():
            raise ValueError("The first and the last tokens must be quotes!")
        super().__init__(tokens)

    def non_preprocessed_repr(self, repr_config):
        if NonEngContent in repr_config.types_to_be_repr and self.has_non_eng_content():
            return ["\"", placeholders['non_eng_content'], "\""]
        else:
            return torepr(self.subtokens, repr_config)

    def preprocessed_repr(self, repr_config) -> List[str]:
        return [placeholders['string_literal']]
