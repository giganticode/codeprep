# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import List

from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.util import ClassNotFound

from codeprep.parse import matchers
from codeprep.parse.matchers import DefaultMatcher
from codeprep.tokens.rootclasses import ParsedToken

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


def convert_text(text: str, extension: str) -> List[ParsedToken]:
    extension = extension or 'java'
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