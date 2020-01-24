# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

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
    """
    >>> replace_non_ascii_seqs("","\xf7")
    ''

    >>> replace_non_ascii_seqs("Ü", "\xf7")
    '\xf7'

    >>> replace_non_ascii_seqs("Üüø", "\xf7")
    '\xf7'

    >>> replace_non_ascii_seqs("abcd", "\xf7")
    'abcd'

    >>> replace_non_ascii_seqs("aæbñńcdú", "\xf7")
    'a\xf7b\xf7cd\xf7'

    >>> replace_non_ascii_seqs("any_string", "\xf7\xa0")
    Traceback (most recent call last):
    ...
    ValueError: Placeholder should be a single character, but is ÷\xa0
    """
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