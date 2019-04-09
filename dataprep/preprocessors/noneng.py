import logging

from dataprep.model.containers import ProcessableTokenContainer
from dataprep.model.noneng import NonEng
from dataprep.model.word import Word

logger = logging.getLogger(__name__)


def is_non_eng(word):
    return not __isascii(word)


def __isascii(str):
    try:
        str.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def mark(token_list):
    return [
        apply_operation_to_token(token, lambda t, c: c(t) if is_non_eng(t.get_canonic_form()) else t)
        for token in token_list]


# TODO merge this with similar function in split.py
def apply_operation_to_token(token, func):
    if isinstance(token, Word):
        return func(token, NonEng)
    elif isinstance(token, ProcessableTokenContainer):
        parts = []
        for subtoken in token.get_subtokens():
            parts.append(apply_operation_to_token(subtoken, func))
        return type(token)(parts)
    else:
        return token
