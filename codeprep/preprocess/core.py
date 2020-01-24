# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Tuple, List, Sequence

from codeprep.preprocess.metadata import PreprocessingMetadata
from codeprep.preprocess.reprconfig import ReprConfig
from codeprep.tokens.rootclasses import ParsedToken


def to_repr_list(token_list: Sequence[ParsedToken], repr_config: ReprConfig) \
        -> Tuple[List[str], PreprocessingMetadata]:
    repr_res = []
    all_metadata = PreprocessingMetadata()
    for token in token_list:
        repr_token, metadata = torepr(token, repr_config)
        repr_res.extend(repr_token)
        all_metadata.update(metadata)
    return repr_res, all_metadata


def torepr(token, repr_config) -> Tuple[List[str], PreprocessingMetadata]:
    clazz = type(token)
    if clazz == str:
        raise AssertionError('Strings are not allowed any more as a result of parsing')
    if clazz == list:
        return to_repr_list(token, repr_config)
    if repr_config and clazz in repr_config.types_to_be_repr:
        return token.preprocessed_repr(repr_config)
    else:
        non_prep, metadata = token.non_preprocessed_repr(repr_config)
        return (non_prep if isinstance(non_prep, list) else [non_prep]), metadata