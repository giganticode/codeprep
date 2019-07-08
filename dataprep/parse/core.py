import logging

from pygments.util import ClassNotFound
from typing import List

from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer

from dataprep.parse import matchers
from dataprep.parse.matchers import DefaultMatcher
from dataprep.parse.model.core import ParsedToken

logger = logging.getLogger(__name__)

matchers = [
    matchers.NewLineMatcher(),
    matchers.TabMatcher(),
    matchers.WhitespaceMatcher(),
    matchers.OperatorMatcher(),
    matchers.NumberMatchers(),
    matchers.WordMatcher(),
    matchers.GenericLiteralMatcher(),
    matchers.KeywordMatcher(),
    matchers.StringMatcher(),
    matchers.OneLineCommentMatcher(),
    matchers.MultiLineLineCommentMatcher(),
    matchers.GenericTokenMatcher()
]


def _convert(token, value: str) -> List[ParsedToken]:
    for matcher in matchers:
        if matcher.match(token, value):
            return matcher.transform(value)

    if DefaultMatcher().match(token, value):
        return DefaultMatcher().transform(value)

    assert False


def convert_text(text: str, extension: str=None) -> List[ParsedToken]:
    if extension:
        try:
            lexer = get_lexer_by_name(extension)
        except ClassNotFound as err:
            logger.warning(err)
            lexer = guess_lexer(text)
    else:
        lexer = guess_lexer(text)
    for token, value in lex(text, lexer):
        model_tokens = _convert(token, value)
        for mr in model_tokens:
            yield mr
