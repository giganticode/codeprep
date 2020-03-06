# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Sequence

from codeprep.preprocess.reprconfig import ReprConfig
from codeprep.preprocess.result import PreprocessingResult
from codeprep.tokentypes.rootclasses import ParsedToken


def to_repr_list(token_list: Sequence[ParsedToken], repr_config: ReprConfig) -> PreprocessingResult:
    total_preprocessing_result = PreprocessingResult()
    for token in token_list:
        preprocessing_result = torepr(token, repr_config)
        total_preprocessing_result.update_(preprocessing_result)
    return total_preprocessing_result


def torepr(token, repr_config) -> PreprocessingResult:
    clazz = type(token)
    if clazz == str:
        raise AssertionError('Strings are not allowed any more as a result of parsing')
    if clazz == list:
        return to_repr_list(token, repr_config)
    if repr_config and clazz in repr_config.types_to_be_repr:
        return token.preprocessed_repr(repr_config)
    else:
        return token.non_preprocessed_repr(repr_config)