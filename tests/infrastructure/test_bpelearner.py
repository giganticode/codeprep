# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from unittest import mock

import pytest

from codeprep.bpepkg.bpe_config import BpeConfig, BpeParam, BpeConfigNotSupported
from codeprep.pipeline.bpelearner import run


@mock.patch('codeprep.pipeline.bpelearner.Dataset', autospec=True)
def test_run_word_end(mocked_dataset):
    bpe_config = BpeConfig({
        BpeParam.BASE: 'code',
        BpeParam.WORD_END: True,
        BpeParam.UNICODE: 'yes',
        BpeParam.CASE: 'yes'
    })
    with pytest.raises(BpeConfigNotSupported):
        run(mocked_dataset, 1, bpe_config)


@mock.patch('codeprep.pipeline.bpelearner.Dataset', autospec=True)
def test_run_bytes_bpe(mocked_dataset):
    bpe_config = BpeConfig({
        BpeParam.BASE: 'code',
        BpeParam.WORD_END: False,
        BpeParam.UNICODE: 'bytes',
        BpeParam.CASE: 'yes'
    })
    with pytest.raises(BpeConfigNotSupported):
        run(mocked_dataset, 1, bpe_config)