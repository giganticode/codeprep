from unittest import mock

import pytest

from dataprep.bpepkg.bpe_config import BpeConfig, BpeParam, BpeConfigNotSupported
from dataprep.pipeline.bpelearner import run


@mock.patch('dataprep.pipeline.bpelearner.Dataset', autospec=True)
def test_run_word_end(mocked_dataset):
    bpe_config = BpeConfig({
        BpeParam.BASE: 'code',
        BpeParam.WORD_END: True,
        BpeParam.UNICODE: 'yes',
        BpeParam.CASE: 'yes'
    })
    with pytest.raises(BpeConfigNotSupported):
        run(mocked_dataset, 1, bpe_config)


@mock.patch('dataprep.pipeline.bpelearner.Dataset', autospec=True)
def test_run_bytes_bpe(mocked_dataset):
    bpe_config = BpeConfig({
        BpeParam.BASE: 'code',
        BpeParam.WORD_END: False,
        BpeParam.UNICODE: 'bytes',
        BpeParam.CASE: 'yes'
    })
    with pytest.raises(BpeConfigNotSupported):
        run(mocked_dataset, 1, bpe_config)
