from pygments.token import Token
from typing import List

import regex

from dataprep.model.chars import NewLine, Tab
from dataprep.model.containers import StringLiteral, OneLineComment
from dataprep.model.core import ParseableToken, ParsedToken
from dataprep.preprocessors.java import process_number_literal
from dataprep.preprocessors.split import simple_split_token


def split_string_tokens(s: str) -> List[str]:
    return [m[0] for m in regex.finditer("((?:_|[0-9]|[[:upper:]]|[[:lower:]])+|[^ ])", s)]


def split_string(s: str):
    return [simple_split_token(ParseableToken(s)) if is_identifier(s) else s for s in split_string_tokens(s)]


def is_identifier(s: str) -> bool:
    return regex.fullmatch("(_|[0-9]|[[:lower:]]|[[:upper:]])+", s)


class DefaultMatcher(object):
    def match(self, token, value: str) -> bool:
        return True

    def transform(self, value: str) -> List[ParsedToken]:
        return split_string(value)


class StringMatcher(object):
    def match(self, token, value: str) -> bool:
        return token is Token.Literal.String

    def transform(self, value: str):
        return [StringLiteral([split_string(value)])]


class CommentMatcher(object):
    def match(self, token, value: str) -> bool:
        return token is Token.Comment.Single

    def transform(self, value: str) -> List[ParsedToken]:
        return [OneLineComment([split_string(value)])]


class WordMatcher(object):
    def match(self, token, value: str) -> bool:
        return token in Token.Name

    def transform(self, value: str) -> List[ParsedToken]:
        return split_string(value)


class KeywordMatcher(object):
    def match(self, token, value: str) -> bool:
        return token in Token.Keyword

    def transform(self, value: str) -> List[ParsedToken]:
        return [simple_split_token(ParseableToken(value))]


class NewLineMatcher(object):
    def match(self, token, value: str) -> bool:
        return value == '\n'

    def transform(self, value: str) -> List[ParsedToken]:
        return [NewLine()]


class WhitespaceMatcher(object):
    def match(self, token, value: str) -> bool:
        return value.strip() == ''

    def transform(self, value: str) -> List[ParsedToken]:
        return [Tab()] * (len(value) // 4)


class TabMatcher(object):
    def match(self, token, value: str) -> bool:
        return value == '\t'

    def transform(self, value: str) -> List[ParsedToken]:
        return [Tab()]


class NumberMatchers(object):
    def match(self, token, value: str) -> bool:
        return token in Token.Literal.Number

    def transform(self, value: str) -> List[ParsedToken]:
        return [process_number_literal(value)]


class OperatorMatcher(object):
    def match(self, token, value: str):
        return token is Token.Operator or token in Token.Punctuation

    def transform(self, value: str) -> List[ParsedToken]:
        return [value]


class WordOperatorMatcher(object):
    def match(self, token, value: str):
        return token is Token.Operator.Word

    def transform(self, value: str) -> List[ParsedToken]:
        return split_string(value)
