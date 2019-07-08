from pygments.token import Token
from typing import List, Union

from dataprep.parse.model.containers import StringLiteral, OneLineComment, MultilineComment
from dataprep.parse.model.core import ParsedToken
from dataprep.parse.model.numeric import Number
from dataprep.parse.model.whitespace import NewLine, Tab
from dataprep.parse.subtokens import split_string


class DefaultMatcher(object):
    def match(self, token, value: str) -> bool:
        return True

    def transform(self, value: str) -> List[Union[str, ParsedToken]]:
        return split_string(value)


class GenericTokenMatcher(object):
    def match(self, token, value: str) -> bool:
        return token in Token.Generic

    def transform(self, value: str) -> List[Union[str, ParsedToken]]:
        return split_string(value)


class StringMatcher(object):
    def match(self, token, value: str) -> bool:
        return token in Token.Literal.String

    def transform(self, value: str) -> List[StringLiteral]:
        return [StringLiteral(split_string(value))]


class OneLineCommentMatcher(object):
    def match(self, token, value: str) -> bool:
        return token is Token.Comment.Single

    def transform(self, value: str) -> List[OneLineComment]:
        return [OneLineComment(split_string(value))]


class MultiLineLineCommentMatcher(object):
    def match(self, token, value: str) -> bool:
        return token in Token.Comment and not token is Token.Comment.Single

    def transform(self, value: str) -> List[MultilineComment]:
        return [MultilineComment(split_string(value))]


class WordMatcher(object):
    def match(self, token, value: str) -> bool:
        return token in Token.Name

    def transform(self, value: str) -> List[Union[str, ParsedToken]]:
        return split_string(value)


class GenericLiteralMatcher(object):
    def match(self, token, value: str) -> bool:
        return token is Token.Literal or token is Token.Literal.Date

    def transform(self, value: str) -> List[Union[str, ParsedToken]]:
        return split_string(value)


class KeywordMatcher(object):
    def match(self, token, value: str) -> bool:
        return token in Token.Keyword

    def transform(self, value: str) -> List[Union[str, ParsedToken]]:
        return [value]
        # return [simple_split_token(ParseableToken(value))]


class NewLineMatcher(object):
    def match(self, token, value: str) -> bool:
        return value == '\n'

    def transform(self, value: str) -> List[NewLine]:
        return [NewLine()]


class WhitespaceMatcher(object):
    def match(self, token, value: str) -> bool:
        return value.strip() == ''

    def transform(self, value: str) -> List[Tab]:
        return [Tab()] * (len(value) // 4)


class TabMatcher(object):
    def match(self, token, value: str) -> bool:
        return value == '\t'

    def transform(self, value: str) -> List[Tab]:
        return [Tab()]


class NumberMatchers(object):
    def match(self, token, value: str) -> bool:
        return token in Token.Literal.Number

    def transform(self, value: str) -> List[Number]:
        return [Number([ch for ch in value])]


class OperatorMatcher(object):
    def match(self, token, value: str):
        return token is Token.Operator or token in Token.Punctuation

    def transform(self, value: str) -> List[str]:
        return [value]


class WordOperatorMatcher(object):
    def match(self, token, value: str):
        return token is Token.Operator.Word

    def transform(self, value: str) -> List[Union[str, ParsedToken]]:
        return split_string(value)
