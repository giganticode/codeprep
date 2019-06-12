import logging

logger = logging.getLogger(__name__)


def is_non_eng(word):
    return not __isascii(word)


def __isascii(str):
    try:
        str.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False
