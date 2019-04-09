import importlib
import logging
import time

from dataprep.model.chars import NewLine
from dataprep.model.word import ParseableToken

logger = logging.getLogger(__name__)


def from_lines(lines):
    return [w for line in lines for w in
            (ParseableToken(line if len(line) > 0 and line[-1] != '\n' else line[:-1]), NewLine())]


def from_string(str):
    return from_lines(str.split('\n'))[:-1]


def from_list(lst):
    return list(map(lambda x: ParseableToken(x), lst))


def names_to_functions(pp_names):
    pps = []
    for name in pp_names:
        file_name, func_name = name[0:name.rindex(".")], name[name.rindex(".")+1:]
        file = importlib.import_module('dataprep.preprocessors.' + file_name)
        func = getattr(file, func_name)
        pps.append(func)
    return pps


def apply_preprocessors(to_be_processed, preprocessors):
    if not preprocessors:
        return to_be_processed
    if isinstance(next(iter(preprocessors)), str):
        preprocessors = names_to_functions(preprocessors)
    for preprocessor in preprocessors:
        start = time.time()
        to_be_processed = preprocessor(to_be_processed)
        t = int(time.time() - start)
        if t > 0:
            logger.debug(f"{preprocessor}: {t}s")
    return to_be_processed
