import regex
from typing import Union, List

from dataprep.model.chars import NewLine, Tab
from dataprep.model.containers import SplitContainer
from dataprep.model.core import ParsedToken
from dataprep.model.noneng import NonEng
from dataprep.model.word import Underscore, Word
from dataprep.preprocessors.noneng import is_non_eng


def wrap_in_noneng_if_needed(s: str):
    return NonEng(Word.from_(s)) if is_non_eng(s) else Word.from_(s)


def split_identifier(token: str):
    parts = [m[0] for m in
             regex.finditer('(_|[0-9]+|[[:upper:]]?[[:lower:]]+|[[:upper:]]+(?![[:lower:]]))', token)]

    processable_tokens = [wrap_in_noneng_if_needed(p) if p != '_' else Underscore() for p in parts]
    return SplitContainer(processable_tokens)


def to_parsed_token_if_needed(param: str) -> Union[str, ParsedToken]:
    if param == '\n':
        return NewLine()
    elif param == '\t' or param == ' ' * 4:
        return Tab()
    elif is_identifier(param):
        return split_identifier(param)
    else:
        return param


def split_string(s: str) -> List[str]:
    return [to_parsed_token_if_needed(m[0]) for m in regex.finditer("((?:_|[0-9]|[[:upper:]]|[[:lower:]])+|[^ ]|    )", s)]


def is_identifier(s: str) -> bool:
    if not isinstance(s, str):
        return False

    # Theoretically for simplicity we allow identifiers starting with digits and don't raise any error if this happens,
    # however leading digits in most cases will be identified as numeric literals on parsing stage
    return regex.fullmatch("(_|[0-9]|[[:lower:]]|[[:upper:]])+", s)