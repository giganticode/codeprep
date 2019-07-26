"""
This module encapsulate all the tricky ilogic of encoding preprocessing options into e.g. 30100
"""

import logging
import sys
from enum import Enum
from typing import Dict, List, Type, Optional

from dataprep.bpepkg.bpe_encode import BpeData, get_bpe_subwords
from dataprep.parse.model.containers import SplitContainer, StringLiteral, OneLineComment, MultilineComment
from dataprep.parse.model.noneng import NonEng
from dataprep.parse.model.numeric import Number
from dataprep.parse.model.whitespace import NewLine, Tab
from dataprep.parse.model.word import Word
from dataprep.preprocess.core import ReprConfig, Splitter

logger = logging.getLogger(__name__)


class PrepParam(str, Enum):
    EN_ONLY: str = 'enonly'
    COM: str = 'com'
    STR: str = 'str'
    SPLIT: str = 'split'
    TABS_NEWLINES: str = 'tabsnewlines'
    CASE: str = 'caps'


def get_possible_str_values() -> List[str]:
    RANGES = [(48, 58), (65, 91), (97, 123)]
    return list(map(lambda x: chr(x), [e for r in RANGES for e in list(range(*r))]))


def get_max_str_length(ch: str) -> Optional[int]:
    num = get_possible_str_values().index(ch)
    if num == 0:
        return None
    elif num == 1:
        return sys.maxsize
    else:
        return num


class PrepConfig(object):
    possible_param_values = {
        PrepParam.EN_ONLY: ['u', 'U'],
        PrepParam.COM: ['0', 'c'],
        PrepParam.STR: get_possible_str_values(),
        PrepParam.SPLIT: ['0', 'F', '1', '2', '3', 's', '4', '5', '6', '7', '8', '9'],
        PrepParam.TABS_NEWLINES: ['s', '0'],
        PrepParam.CASE: ['u', 'l'],
    }

    human_readable_values = {
        PrepParam.EN_ONLY: {'u': 'multilang',
                            'U': 'asci_only'},
        PrepParam.COM: {'0': 'NO_comments',
                            'c': 'comments'},
        PrepParam.STR: {k: k for k in get_possible_str_values()},
        PrepParam.SPLIT: {'0': 'NO_splitting',
                          'F': 'No splitting + full strings',
                          '1': 'camel+underscore',
                          '2': 'camel+underscore+numbers',
                          '3': 'numbers+ronin',
                          's': 'camel+underscore+numbers+stemming',
                          '4': 'camel+underscore+bpe_5k',
                          '5': 'camel+underscore+bpe_1k',
                          '6': 'camel+underscore+bpe_10k',
                          '7': 'camel+underscore+bpe_20k',
                          '8': 'camel+underscore+bpe_0',
                          '9': 'camel+underscore+bpe_custom'},
        PrepParam.TABS_NEWLINES: {'s': 'tabs+newlines',
                                  '0': 'NO_tabs+NO_newlines'},
        PrepParam.CASE: {
            'u': 'case_preserved',
            'l': 'lowercased'
        }
    }

    base_bpe_mask = {
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '1',
        PrepParam.TABS_NEWLINES: 's',
    }

    @staticmethod
    def __check_param_number(n_passed_params: int):
        n_expected_params = len([i for i in PrepParam])
        if n_passed_params != n_expected_params:
            raise ValueError(f'Expected {n_expected_params} params, got {n_passed_params}')

    @classmethod
    def from_encoded_string(cls, s: str):
        PrepConfig.__check_param_number(len(s))

        res = {}
        for ch, pp in zip(s, PrepParam):
            res[pp] = ch
        return cls(res)

    @staticmethod
    def __check_invariants(params: Dict[PrepParam, str]):
        PrepConfig.__check_param_number(len(params))
        for pp in PrepParam:
            if params[pp] not in PrepConfig.possible_param_values[pp]:
                raise ValueError(f'Invalid value {params[pp]} for prep param {pp}, '
                                 f'possible values are: {PrepConfig.possible_param_values[pp]}')

        if params[PrepParam.CASE] == 'l' and params[PrepParam.SPLIT] in ['0', 'F']:
            raise ValueError("Combination NOSPLIT and LOWERCASED is not supported: "
                             "basic splitting needs to be dont done to lowercase the subword.")

        if params[PrepParam.CASE] == 'u' and params[PrepParam.SPLIT] == 's':
            raise ValueError("Combination STEMMING and UPPERCASE is not supported: "
                             "stemmer always lowercases words.")


    def __init__(self, params: Dict[PrepParam, str]):
        PrepConfig.__check_invariants(params)

        self.params = params

    def __str__(self) -> str:
        res = ""
        for k in PrepParam:
            res += self.params[k]
        return res

    def __repr__(self):
        return str(self.params)

    def get_param_value(self, param: PrepParam) -> str:
        return self.params[param]

    def get_base_bpe_prep_config(self):
        res = PrepConfig.base_bpe_mask
        res[PrepParam.CASE] = self.params[PrepParam.CASE]
        return str(PrepConfig(res))

    def __eq__(self, other):
        return self.params == other.params

    def get_number_splitter(self) -> Splitter:
        split_param_value = self.get_param_value(PrepParam.SPLIT)
        if split_param_value in ['0', 'F', '1']:
            return lambda s,c: [s]
        elif split_param_value in ['2', '3', 's']:
            return lambda s,c: [ch for ch in s]
        elif split_param_value in ['4', '5', '6', '7', '8', '9']:
            return lambda s,c: get_bpe_subwords(s, c)
        else:
            raise ValueError(f"Invalid SPLIT param value: {split_param_value}")

    def get_word_splitter(self) -> Optional[Splitter]:
        split_param_value = self.get_param_value(PrepParam.SPLIT)
        if split_param_value in ['4', '5', '6', '7', '8', '9']:
            return lambda s, c: get_bpe_subwords(s, c)
        elif split_param_value in ['1', '2']:
            return lambda s,c: [s]
        elif split_param_value == '3':
            from spiral import ronin
            return lambda s, c: ronin.split(s)
        elif split_param_value == 's':
            from dataprep.stemming import stem
            from spiral import ronin
            return lambda s,c: list(map(lambda ss: stem(ss), ronin.split(s)))
        elif split_param_value in ['0', 'F']:
            return None
        else:
            raise ValueError(f"Invalid SPLIT param value: {split_param_value}")

    def get_types_to_be_repr(self) -> List[Type]:
        res = []
        if self.get_param_value(PrepParam.SPLIT) in ['1', '2', '3', '4', '5', '6', '7', '8', '9', 's']:
            res.extend([SplitContainer, Word])
        if self.get_param_value(PrepParam.SPLIT) in ['2', '3', '4', '5', '6', '7', '8', '9', 's']:
            res.append(Number)
        if self.get_param_value(PrepParam.COM) == '0':
            res.extend([OneLineComment, MultilineComment])
        if self.get_param_value(PrepParam.STR) == '0':
            res.append(StringLiteral)
        if self.get_param_value(PrepParam.EN_ONLY) == 'U':
            res.append(NonEng)
        if self.get_param_value(PrepParam.TABS_NEWLINES) == '0':
            res.extend([NewLine, Tab])
        return res

    def get_repr_config(self, bpe_data: Optional[BpeData]):
        return ReprConfig(self.get_types_to_be_repr(),
                          bpe_data,
                          self.get_param_value(PrepParam.CASE) == 'l',
                          self.get_number_splitter(),
                          self.get_word_splitter(),
                          self.get_param_value(PrepParam.SPLIT) == 'F',
                          get_max_str_length(self.get_param_value(PrepParam.STR)))

    def is_bpe(self):
        """
        Check if this config corresponds to preprocessing with BPE.
        Note: splitting into chars is implemented as BPE with 0 merges, so in this case this method will also return True.

        :return: True if this config corresponds to preprocessing with BPE, False otherwise.
        """
        return self.get_param_value(PrepParam.SPLIT) in ['4', '5', '6', '7', '8', '9']

    #TODO make use of basic_bpe mask
    def is_base_bpe_config(self):
        return self.get_param_value(PrepParam.COM) == 'c' \
               and self.get_param_value(PrepParam.STR) == '1' \
               and self.get_param_value(PrepParam.SPLIT) == '1' \
               and self.get_param_value(PrepParam.TABS_NEWLINES) == 's'
