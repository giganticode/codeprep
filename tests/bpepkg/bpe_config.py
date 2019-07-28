import unittest

from dataprep.bpepkg.bpe_config import BpeConfig, BpeParam


class BpeConfigToSuffixTest(unittest.TestCase):
    def test_no_suffix(self):
        bpe_config = BpeConfig({
            BpeParam.CASE: 'yes',
            BpeParam.WORD_END: False,
            BpeParam.BASE: 'all',
            BpeParam.UNICODE: 'yes'
        })

        actual = bpe_config.to_suffix()

        self.assertEqual("", actual)

    def test_nocase_wordend_nounicode(self):
        bpe_config = BpeConfig({
            BpeParam.CASE: 'no',
            BpeParam.WORD_END: True,
            BpeParam.BASE: 'all',
            BpeParam.UNICODE: 'no'
        })

        actual = bpe_config.to_suffix()

        self.assertEqual("nocase_we_nounicode", actual)

    def test_prefix_bytes(self):
        bpe_config = BpeConfig({
            BpeParam.CASE: 'prefix',
            BpeParam.WORD_END: False,
            BpeParam.BASE: 'all',
            BpeParam.UNICODE: 'bytes'
        })

        actual = bpe_config.to_suffix()

        self.assertEqual("prefix_bytes", actual)


if __name__ == '__main__':
    unittest.main()