# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum
from typing import Dict

from codeprep.prepconfig import PrepConfig, PrepParam


class BpeConfigNotSupported(Exception):
    pass


class BpeParam(str, Enum):
    CASE: str = 'case'
    WORD_END: str = 'wordend'
    BASE: str = 'base'
    UNICODE: str = 'unicode'


class BpeConfig(object):
    possible_param_values = {
        BpeParam.CASE: ['yes'],
        BpeParam.WORD_END: [True, False],
        BpeParam.BASE: ["all", "code", "java"],
        BpeParam.UNICODE: ['yes', 'no', 'bytes'],
    }

    @staticmethod
    def _check_param_number(n_passed_params: int):
        n_expected_params = len([i for i in BpeParam])
        if n_passed_params != n_expected_params:
            raise ValueError(f'Expected {n_expected_params} params, got {n_passed_params}')

    @staticmethod
    def _check_invariants(params: Dict[BpeParam, str]):
        BpeConfig._check_param_number(len(params))
        for pp in BpeParam:
            if params[pp] not in BpeConfig.possible_param_values[pp]:
                raise ValueError(f'Invalid value {params[pp]} for prep param {pp}, '
                                 f'possible values are: {BpeConfig.possible_param_values[pp]}')

    def __init__(self, params: Dict[BpeParam, str]):
        BpeConfig._check_invariants(params)

        self.params = params

    def get_param_value(self, param: BpeParam) -> str:
        return self.params[param]

    def to_prep_config(self):
        return PrepConfig({
            PrepParam.EN_ONLY: 'U' if self.get_param_value(BpeParam.UNICODE) == 'no' else 'u',
            PrepParam.COM: '0',
            PrepParam.STR: 'E',
            PrepParam.SPLIT: 'F',
            PrepParam.TABS_NEWLINES: 's',
            PrepParam.CASE: 'u'
        })

    UNICODE_NO = 'nounicode'
    UNICODE_BYTES = 'bytes'
    CASE_NO = 'nocase'
    CASE_PREFIX = 'prefix'
    WORD_END = 'we'

    @staticmethod
    def from_suffix(suffix: str):
        if suffix.find(BpeConfig.CASE_NO) != -1:
            case = 'no'
        elif suffix.find(BpeConfig.CASE_PREFIX) != -1:
            case = 'prefix'
        else:
            case = 'yes'

        if suffix.find(BpeConfig.UNICODE_NO) != -1:
            unicode = 'no'
        elif suffix.find(BpeConfig.UNICODE_BYTES) != -1:
            unicode = 'bytes'
        else:
            unicode = 'yes'


        return BpeConfig({
            BpeParam.CASE: case,
            BpeParam.WORD_END: suffix.find(BpeConfig.WORD_END) != -1,
            BpeParam.BASE: 'code',
            BpeParam.UNICODE: unicode,
        })

    def to_suffix(self):
        """
        >>> bpe_config = BpeConfig({
        ...     BpeParam.CASE: 'yes',
        ...     BpeParam.WORD_END: False,
        ...     BpeParam.BASE: 'all',
        ...     BpeParam.UNICODE: 'yes'
        ... })
        >>> bpe_config.to_suffix()
        ''

        >>> bpe_config = BpeConfig({
        ...     BpeParam.CASE: 'yes',
        ...     BpeParam.WORD_END: True,
        ...     BpeParam.BASE: 'all',
        ...     BpeParam.UNICODE: 'no'
        ... })
        >>> bpe_config.to_suffix()
        'we_nounicode'

        >>> bpe_config = BpeConfig({
        ...     BpeParam.CASE: 'yes',
        ...     BpeParam.WORD_END: False,
        ...     BpeParam.BASE: 'all',
        ...     BpeParam.UNICODE: 'bytes'
        ... })
        >>> bpe_config.to_suffix()
        'bytes'

        """
        suffix_parts = []

        if self.get_param_value(BpeParam.CASE) == 'no':
            suffix_parts.append(BpeConfig.CASE_NO)
        elif self.get_param_value(BpeParam.CASE) == 'prefix':
            suffix_parts.append(BpeConfig.CASE_PREFIX)

        if self.get_param_value(BpeParam.WORD_END):
            suffix_parts.append(BpeConfig.WORD_END)

        if self.get_param_value(BpeParam.UNICODE) == 'no':
            suffix_parts.append(BpeConfig.UNICODE_NO)
        elif self.get_param_value(BpeParam.UNICODE) == 'bytes':
            suffix_parts.append(BpeConfig.UNICODE_BYTES)

        return "_".join(suffix_parts)

    def __eq__(self, other):
        return self.params == other.params

    def __str__(self) -> str:
        parts = [str(self.params[k]) for k in BpeParam]
        return "_".join(parts)

    def __repr__(self):
        return str(self.params)