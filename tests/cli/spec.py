import unittest
from unittest import mock

from docopt import DocoptExit
from unittest.mock import Mock

from dataprep.bpepkg.bpe_config import BpeConfig, BpeParam
from dataprep.cli.spec import parse_and_run
from dataprep.prepconfig import PrepParam, PrepConfig


@mock.patch('dataprep.cli.impl.dataprep.api')
class ParseAndRunTest(unittest.TestCase):

    def test_u001u(self, api_mock):
        argv = ['nosplit', 'str', '--no-spaces']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '0',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'u'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_U000u(self, api_mock):
        argv = ['nosplit', 'str', '--no-spaces', '--no-unicode']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'U',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '0',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'u'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_x20xx(self, api_mock):
        argv = ['nosplit', 'str', '--no-spaces', '--no-str', '--no-com']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '2',
            PrepParam.SPLIT: '0',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'u'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_xx0sx(self, api_mock):
        argv = ['nosplit', 'str']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '0',
            PrepParam.TABS_NEWLINES: 's',
            PrepParam.CASE: 'u'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_xx0x1(self, api_mock):
        argv = ['nosplit', 'str', '--no-spaces', '--no-case']
        with self.assertRaises(DocoptExit) as context:
            parse_and_run(argv)

    def test_u010l(self, api_mock):
        argv = ['basic', 'str', '--no-spaces', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '1',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_Ux1xx(self, api_mock):
        argv = ['basic', 'str', '--no-spaces', '--no-case', '--no-unicode']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'U',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '1',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_x11xx(self, api_mock):
        argv = ['basic', 'str', '--no-spaces', '--no-case', '--no-str']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '1',
            PrepParam.SPLIT: '1',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_x21xx(self, api_mock):
        argv = ['basic', 'str', '--no-spaces', '--no-case', '--no-str', '--no-com']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '2',
            PrepParam.SPLIT: '1',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_x31xx(self, api_mock):
        argv = ['basic', 'str', '--no-spaces', '--no-case', '--no-com']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '3',
            PrepParam.SPLIT: '1',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_u02xx(self, api_mock):
        argv = ['basic', 'str', '--no-spaces', '--no-case', '--split-numbers']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '2',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_u03xx(self, api_mock):
        argv = ['ronin', 'str', '--no-spaces']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '3',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'u'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_xx3xl(self, api_mock):
        with self.assertRaises(DocoptExit):
            argv = ['ronin', 'str', '--no-spaces', '--no-case']
            parse_and_run(argv)

    def test_u0sxx(self, api_mock):
        argv = ['basic', 'str', '--no-spaces', '--stem']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: 's',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_u04xx(self, api_mock):
        argv = ['bpe', '5k', 'str', '--no-spaces', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '4',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, '5k')

    def test_u05xx(self, api_mock):
        argv = ['bpe', '1k', 'str', '--no-spaces', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '5',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, '1k')

    def test_xx6xx(self, api_mock):
        argv = ['bpe', '10k', 'str', '--no-spaces', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '6',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, '10k')

    def test_xx9xx(self, api_mock):
        argv = ['bpe', 'custom-id-5000', 'str', '--no-spaces', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '9',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, 'custom-id-5000')

    def test_xx8xx(self, api_mock):
        argv = ['chars', 'str', '--no-spaces', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '8',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_xx1sx(self, api_mock):
        argv = ['basic', 'str', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '1',
            PrepParam.TABS_NEWLINES: 's',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_xx1xu(self, api_mock):
        argv = ['basic', 'str', '--no-spaces']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '1',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'u'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)

    def test_path(self, api_mock):
        argv = ['nosplit', '--path', '/path/to/dataset', '--no-spaces']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '0',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'u'
        })
        api_mock.corpus.preprocess_corpus.assert_called_with('/path/to/dataset', prep_config, None, calc_vocab=False, extensions=None, output_path=None)

    def test_path_short(self, api_mock):
        argv = ['nosplit', '-p', '/path/to/dataset', '--no-spaces']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '0',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'u'
        })
        api_mock.corpus.preprocess_corpus.assert_called_with('/path/to/dataset', prep_config, None, calc_vocab=False,
                                                             extensions=None, output_path=None)

    def test_output_and_vocab(self, api_mock):
        argv = ['nosplit', '--path', '/path/to/dataset', '--output-path', '/path/to/output', '--no-spaces', '--calc-vocab']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '0',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'u'
        })
        api_mock.corpus.preprocess_corpus.assert_called_with('/path/to/dataset', prep_config, None,
                                                             calc_vocab=True, extensions=None, output_path='/path/to/output')


    def test_output_and_vocab_short(self, api_mock):
        argv = ['nosplit', '--path', '/path/to/dataset', '-o', '/path/to/output', '--no-spaces', '-V']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '0',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'u'
        })
        api_mock.corpus.preprocess_corpus.assert_called_with('/path/to/dataset', prep_config, None,
                                                             calc_vocab=True, extensions=None, output_path='/path/to/output')

    def test_output_with_text(self, api_mock):
        argv = ['nosplit', 'str', '-o', '/path/to/output', '--no-spaces']
        with self.assertRaises(DocoptExit) as context:
            parse_and_run(argv)

    def test_all_short_config_options(self, api_mock):
        argv = ['basic', 'str', '-0lSCU']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'U',
            PrepParam.COM_STR: '2',
            PrepParam.SPLIT: '1',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.Dataset')
@mock.patch('dataprep.cli.impl.bpelearner')
class ParseAndRunLearnBpeTest(unittest.TestCase):
    def test_yes_false_java_yes(self, bpe_learner_mock, dataset_mock):

        # given
        dataset_mock.create = Mock(return_value=dataset_mock)
        argv = ['learn-bpe', '1000', '-p', '/path/to/dataset', '--legacy']

        # when
        parse_and_run(argv)

        # then
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '1',
            PrepParam.TABS_NEWLINES: 's',
            PrepParam.CASE: 'u'
        })
        bpe_config = BpeConfig({
            BpeParam.CASE: 'yes',
            BpeParam.WORD_END: False,
            BpeParam.BASE: 'java',
            BpeParam.UNICODE: 'yes',
        })
        dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, 'java', None, bpe_config)
        bpe_learner_mock.run.assert_called_with(dataset_mock, 1000, bpe_config)

    def test_no_true_code_no(self, bpe_learner_mock, dataset_mock):

        # given
        dataset_mock.create = Mock(return_value=dataset_mock)
        argv = ['learn-bpe', '1000', '-p', '/path/to/dataset', '--no-case', '--no-unicode', '--word-end']

        # when
        parse_and_run(argv)

        # then
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'U',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '1',
            PrepParam.TABS_NEWLINES: 's',
            PrepParam.CASE: 'l'
        })
        bpe_config = BpeConfig({
            BpeParam.CASE: 'no',
            BpeParam.WORD_END: True,
            BpeParam.BASE: 'code',
            BpeParam.UNICODE: 'no',
        })
        dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None, bpe_config)
        bpe_learner_mock.run.assert_called_with(dataset_mock, 1000, bpe_config)

    def test_prefix_true_code_bytes(self, bpe_learner_mock, dataset_mock):

        # given
        dataset_mock.create = Mock(return_value=dataset_mock)
        argv = ['learn-bpe', '1000', '-p', '/path/to/dataset', '--case-prefix', '--bytes', '--word-end']

        # when
        parse_and_run(argv)

        # then
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'u',
            PrepParam.COM_STR: '0',
            PrepParam.SPLIT: '1',
            PrepParam.TABS_NEWLINES: 's',
            PrepParam.CASE: 'u'
        })
        bpe_config = BpeConfig({
            BpeParam.CASE: 'prefix',
            BpeParam.WORD_END: True,
            BpeParam.BASE: 'code',
            BpeParam.UNICODE: 'bytes',
        })
        dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None, bpe_config)
        bpe_learner_mock.run.assert_called_with(dataset_mock, 1000, bpe_config)


if __name__ == '__main__':
    unittest.main()
