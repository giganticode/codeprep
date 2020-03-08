# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging

from typing import List, Tuple

logger = logging.getLogger(__name__)


def has_one_of_extensions(name: bytes, extensions: List[bytes]) -> bool:
    """
    >>> has_one_of_extensions(b'/home/abc.java', [b'java', b'c'])
    True

    >>> has_one_of_extensions(b'/home/abc.py', [b'java', b'c'])
    False

    >>> has_one_of_extensions(b'/home/abc.dtc', [b'java', b'c'])
    False

    >>> has_one_of_extensions(b'/home/abc.f.java.prep', [b'java.prep', b'c'])
    True

    >>> has_one_of_extensions(b'/home/abc.f.java.prep', [b'a.prep', b'c'])
    False

    """
    for ext in extensions:
        if name.endswith(b'.' + ext):
            return True
    return False


def read_file_contents(file_path: bytes) -> Tuple[List[str], bytes]:
    try:
        return read_file_with_encoding(file_path, 'utf-8')
    except UnicodeDecodeError:
        try:
            return read_file_with_encoding(file_path, 'ISO-8859-1')
        except UnicodeDecodeError:
            logger.error(f"Unicode decode error in file: {file_path}")


def read_file_with_encoding(file_path: bytes, encoding: str) -> Tuple[List[str], bytes]:
    with open(file_path, 'r', encoding=encoding) as f:
        return [line.rstrip('\n') for line in f], file_path