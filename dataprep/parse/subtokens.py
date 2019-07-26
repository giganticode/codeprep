import regex
from typing import Union, List

from dataprep.parse.model.containers import SplitContainer
from dataprep.parse.model.core import ParsedToken
from dataprep.parse.model.noneng import NonEng
from dataprep.parse.model.numeric import Number
from dataprep.parse.model.whitespace import NewLine, Tab, SpaceInString
from dataprep.parse.model.word import Underscore, Word
from dataprep.noneng import is_non_eng


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
    return regex.fullmatch(NUMBER_PATTERN, word) is not None


def to_parsed_token_if_needed(param: str) -> Union[str, ParsedToken]:
    if param == '\n':
        return NewLine()
    elif param == '\t' or param == ' ' * 4:
        return Tab()
    elif is_number(param):
        return Number(param)
    elif is_word(param):
        return split_identifier(param)
    else:
        return param


def to_parsed_string_token_if_needed(param: str) -> Union[str, ParsedToken]:
    if param == '\n':
        return NewLine()
    elif param == '\t':
        return Tab()
    elif regex.fullmatch(" +", param):
        return SpaceInString(n_chars=len(param))
    elif is_number(param):
        return Number(param)
    elif is_word(param):
        return split_identifier(param)
    else:
        return param


def split_string(s: str) -> List[Union[str, ParsedToken]]:
    return [to_parsed_string_token_if_needed(m[0]) for m in regex.finditer("(\\w+|( )+|[^ ])", s)]


def split_into_words(s: str) -> List[Union[str, ParsedToken]]:
    return [to_parsed_token_if_needed(m[0]) for m in regex.finditer("(\\w+|[^ ]|    )", s)]


def is_word(s: str) -> bool:
    if not isinstance(s, str):
        return False

    return regex.fullmatch("\\w+", s)