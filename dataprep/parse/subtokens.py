import regex
from typing import Union, List

from dataprep.parse.model.containers import SplitContainer
from dataprep.parse.model.core import ParsedToken
from dataprep.parse.model.noneng import NonEng
from dataprep.parse.model.whitespace import NewLine, Tab
from dataprep.parse.model.word import Underscore, Word
from dataprep.noneng import is_non_eng


def split_identifier(token: str) -> SplitContainer:
    parts = [m[0] for m in
             regex.finditer('(_|[0-9]+|[[:upper:]]?[[:lower:]]+|[[:upper:]]+(?![[:lower:]])|[^ ])', token)]

    processable_tokens = [Word.from_(p) if p != '_' else Underscore() for p in parts]
    split_container = SplitContainer(processable_tokens)
    return NonEng(split_container) if is_non_eng(token) else split_container


def to_parsed_token_if_needed(param: str) -> Union[str, ParsedToken]:
    if param == '\n':
        return NewLine()
    elif param == '\t' or param == ' ' * 4:
        return Tab()
    elif is_word(param):
        return split_identifier(param)
    else:
        return param


def split_string(s: str) -> List[Union[str, ParsedToken]]:
    return [to_parsed_token_if_needed(m[0]) for m in regex.finditer("(\\w+|[^ ]|    )", s)]


def is_word(s: str) -> bool:
    if not isinstance(s, str):
        return False

    return regex.fullmatch("\\w+", s)