# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
>>> import tempfile
>>> f = tempfile.NamedTemporaryFile(delete=False)
>>> cache = {'ab': ['a', 'b'], '\\t\\xa0': ['\\t', '\\xa0']}
>>> dump_bpe_cache(cache, f.name)
>>> cache == read_bpe_cache(f.name)
True
"""
from typing import List, Dict

from codeprep.util import to_literal_str, to_non_literal_str

KEY_VALUE_DELIM = '\t'
VALUE_PARTS_DELIM = ' '


def read_bpe_cache(file: str) -> Dict[str, List[str]]:
    words = {}
    with open(file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            splits = line.split(KEY_VALUE_DELIM)
            second_column = to_non_literal_str(splits[1]).split(VALUE_PARTS_DELIM)
            words[to_non_literal_str(splits[0])] = second_column
    return words


def dump_bpe_cache(dct: Dict[str, List[str]], file: str) -> None:
    with open(file, 'w') as f:
        for word, subwords in dct.items():
            a = to_literal_str(" ".join(subwords))
            f.write(f'{to_literal_str(str(word))}{KEY_VALUE_DELIM}{a}\n')