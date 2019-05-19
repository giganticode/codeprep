from typing import List

from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer

from dataprep.model.core import ParsedToken
from dataprep.parse import matchers
from dataprep.parse.matchers import DefaultMatcher

matchers = [
    matchers.NewLineMatcher(),
    matchers.TabMatcher(),
    matchers.WhitespaceMatcher(),
    matchers.OperatorMatcher(),
    matchers.NumberMatchers(),
    matchers.WordMatcher(),
    matchers.KeywordMatcher(),
    matchers.StringMatcher(),
    matchers.CommentMatcher(),
]


def _convert(token, value: str) -> List[ParsedToken]:
    for matcher in matchers:
        if matcher.match(token, value):
            return matcher.transform(value)

    if DefaultMatcher().match(token, value):
        return DefaultMatcher().transform(value)

    assert False


def convert_text(text: str, extension: str=None) -> List[ParsedToken]:
    lexer = get_lexer_by_name(extension) if extension else guess_lexer(text)
    for token, value in lex(repr(text)[1:-1], lexer):
        model_tokens = _convert(token, value)
        for mr in model_tokens:
            yield mr
