import unittest
from unittest import mock

from dataprep.bpepkg.bpe_config import BpeConfig, BpeParam, BpeConfigNotSupported
from dataprep.infrastructure.bpelearner import run


@mock.patch('dataprep.infrastructure.bpelearner.Dataset')
class RunTest(unittest.TestCase):

    def test_word_end(self, mocked_dataset):
        bpe_config = BpeConfig({
            BpeParam.BASE: 'code',
            BpeParam.WORD_END: True,
            BpeParam.UNICODE: 'yes',
            BpeParam.CASE: 'yes'
        })
        with self.assertRaises(BpeConfigNotSupported):
            run(mocked_dataset, 1, bpe_config)

    def test_bytes_bpe(self, mocked_dataset):
        bpe_config = BpeConfig({
            BpeParam.BASE: 'code',
            BpeParam.WORD_END: False,
            BpeParam.UNICODE: 'bytes',
            BpeParam.CASE: 'yes'
        })
        with self.assertRaises(BpeConfigNotSupported):
            run(mocked_dataset, 1, bpe_config)

if __name__ == '__main__':
    unittest.main()