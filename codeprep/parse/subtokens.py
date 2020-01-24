# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import List

import regex

from codeprep.noneng import is_non_eng
from codeprep.tokens.containers import SplitContainer
from codeprep.tokens.noneng import NonEng
from codeprep.tokens.numeric import Number
from codeprep.tokens.rootclasses import ParsedToken
from codeprep.tokens.whitespace import NewLine, Tab, SpaceInString
from codeprep.tokens.word import Underscore, Word, NonCodeChar


def split_identifier(token: str) -> SplitContainer:
    parts = [m[0] for m in
             regex.finditer('(_|[0-9]+|[[:upper:]]?[[:lower:]]+|[[:upper:]]+(?![[:lower:]])|[^ ])', token)]

    processable_tokens = [Word.from_(p) if p != '_' else Underscore() for p in parts]
    split_container = SplitContainer(processable_tokens)
    return NonEng(split_container) if is_non_eng(token) else split_container


# Using the same regexps SLP team uses to parse numbers in java code
# https://github.com/SLP-team/SLP-Core/blob/master/src/main/java/slp/core/lexing/code/JavaLexer.java

HEX_REGEX = "0x([0-9a-fA-F]+_)*[0-9a-fA-F]+[lL]?"
BIN_REGEX = "0b([01]+_)*[01]+[lL]?"
IR_REGEX = "([0-9]+_)*[0-9]+[lLfFdD]?"
DBL_REGEXA = "[0-9]+\\.[0-9]+([eE][-+]?[0-9]+)?[fFdD]?"
DBL_REGEXB = "[0-9]+\\.([eE][-+]?[0-9]+)?[fFdD]?"
DBL_REGEXC = "\\.[0-9]+([eE][-+]?[0-9]+)?[fFdD]?"
DBL_REGEXD = "[0-9]+[eE][-+]?[0-9]+[fFdD]?"

NUMBER_PATTERN = f'({HEX_REGEX}|{BIN_REGEX}|{IR_REGEX}|{DBL_REGEXA}|{DBL_REGEXB}|{DBL_REGEXC}|{DBL_REGEXD})'


def is_number(word: str) -> bool:
    """
    >>> is_number("0")
    True

    >>> is_number("8")
    True

    >>> is_number("-5")
    False

    >>> is_number("23450012")
    True

    >>> is_number("283463L")
    True

    >>> is_number("342424242l")
    True

    >>> is_number("0.")
    True

    >>> is_number(".0")
    True

    >>> is_number(".0d")
    True

    >>> is_number("353535.")
    True

    >>> is_number("353535.D")
    True

    >>> is_number(".353535F")
    True

    >>> is_number(".353535f")
    True

    >>> is_number("0.2e+3D")
    True

    >>> is_number("23424.E-30F")
    True

    >>> is_number(".002e-0f")
    True

    >>> is_number("0b10101")
    True

    >>> is_number("0b0011L") # java -- not python
    True

    >>> is_number("0b0")
    True

    >>> is_number("0x8AbCc006EfBd")
    True

    >>> is_number("0xG12")
    False

    >>> is_number("0x56DL")
    True

    >>> is_number("0x56Dl")
    True
    """
    return regex.fullmatch(NUMBER_PATTERN, word) is not None


def to_parsed_token(token: str) -> ParsedToken:
    if token == '\n':
        return NewLine()
    elif token == '\t':
        return Tab()
    elif is_number(token):
        return Number(token)
    elif regex.fullmatch("\\w+", token):
        return split_identifier(token)
    else:
        return NonCodeChar(token)


def split_string(token: str) -> List[ParsedToken]:
    """
    >>> split_string("    var = 9.4\\t\\n")
    [<SpaceInString> (n_chars=4), SplitContainer[Word(('var', none))], \
<SpaceInString> (n_chars=1), NonCodeChar(=), <SpaceInString> (n_chars=1), <Number>(9), \
NonCodeChar(.), <Number>(4), <Tab>, <NewLine>]
    """
    res = []
    arbitrary_whitespace = "( )+"
    for m in regex.finditer(f"(\\w+|[^ ]|{arbitrary_whitespace})", token):
        if regex.fullmatch(arbitrary_whitespace, m[0]):
            res.append(SpaceInString(n_chars=len(m[0])))
        else:
            res.append(to_parsed_token(m[0]))
    return res


def split_into_words(token: str) -> List[ParsedToken]:
    """
    >>> split_into_words("    var = 9.4\\t\\n")
    [<Tab>, SplitContainer[Word(('var', none))], NonCodeChar(=), <Number>(9), \
NonCodeChar(.), <Number>(4), <Tab>, <NewLine>]
    """
    res = []
    four_char_whitespace = " " * 4
    for m in regex.finditer(f"(\\w+|[^ ]|{four_char_whitespace})", token):
        if m[0] == four_char_whitespace:
            res.append(Tab())
        else:
            res.append(to_parsed_token(m[0]))
    return res