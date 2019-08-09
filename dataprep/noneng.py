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


def replace_non_ascii_seqs(word:str, placeholder: str) -> str:
    if len(placeholder) != 1:
        raise ValueError(f"Placeholder should be a single character, but is {placeholder}")

    new_word = ""
    ongoing_non_ascii_seq = False
    for ch in word:
        if ord(ch) < 128:
            if ongoing_non_ascii_seq:
                new_word += placeholder
                ongoing_non_ascii_seq = False
            new_word += ch
        else:
            ongoing_non_ascii_seq = True
    if ongoing_non_ascii_seq:
        new_word += placeholder

    return new_word
