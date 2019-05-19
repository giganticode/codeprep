import importlib
import logging
from typing import List, Union, Callable

import time

from dataprep.model.chars import NewLine
from dataprep.model.core import ParseableToken, ParsedToken
from dataprep.preprocessors.preprocessor_list import pp_params

logger = logging.getLogger(__name__)


def parse_from_string(text: str):
    token_list = from_string(text)
    return _apply_preprocessors(token_list, pp_params["preprocessors"])


def parse_from_lines(lines: List[str]):
    token_list = _from_lines(lines)
    return _apply_preprocessors(token_list, pp_params["preprocessors"])


def from_string(s: str) -> List[Union[ParseableToken, NewLine]]:
    return _from_lines(s.split('\n'))[:-1]


def _from_lines(lines: List[str]) -> List[Union[ParseableToken, NewLine]]:
    for line in lines:
        if line and line[-1] == '\n':
            raise ValueError("Lines cannot terminate with a newline. There's a bug in the upstream code.")

    return [w for line in lines for w in (ParseableToken(line), NewLine())]


def _names_to_functions(pp_names: List[str]) -> List[Callable]:
    pps = []
    for name in pp_names:
        file_name, func_name = name[0:name.rindex(".")], name[name.rindex(".")+1:]
        file = importlib.import_module('dataprep.preprocessors.' + file_name)
        func = getattr(file, func_name)
        pps.append(func)
    return pps


def _apply_preprocessors(to_be_processed: List[Union[ParsedToken, ParseableToken]], preprocessors: List[Union[str, Callable]]) -> List[ParsedToken]:
    if not preprocessors:
        return to_be_processed
    if isinstance(next(iter(preprocessors)), str):
        preprocessors = _names_to_functions(preprocessors)
    for preprocessor in preprocessors:
        start = time.time()
        to_be_processed = preprocessor(to_be_processed)
        t = int(time.time() - start)
        if t > 0:
            logger.debug(f"{preprocessor}: {t}s")
    return to_be_processed
