import unittest
from unittest import mock

from docopt import DocoptExit
from unittest.mock import Mock

from dataprep.bpepkg.bpe_config import BpeConfig, BpeParam
from dataprep.cli.spec import parse_and_run
from dataprep.prepconfig import PrepParam, PrepConfig


@mock.patch('dataprep.cli.impl.api')
class CliTest(unittest.TestCase):

    def test_parse_and_run_00010(self, api_mock):
        argv = ['nosplit', 'str', '--no-spaces']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_from_args_3x0xx(self, api_mock):
        argv = ['nosplit', 'str', '--no-spaces', '--no-unicode']
        parse_and_run(argv)
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 3,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_x20xx(self, api_mock):
        argv = ['nosplit', 'str', '--no-spaces', '--no-str', '--no-com']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 2,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_xx00x(self, api_mock):
        argv = ['nosplit', 'str']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 0,
            PrepParam.CAPS: 0
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_xx0x1(self, api_mock):
        argv = ['nosplit', 'str', '--no-spaces', '--no-case']
        with self.assertRaises(DocoptExit) as context:
            parse_and_run(argv)

    def test_parse_and_run_00111(self, api_mock):
        argv = ['basic', 'str', '--no-spaces', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_3x1xx(self, api_mock):
        argv = ['basic', 'str', '--no-spaces', '--no-case', '--no-unicode']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 3,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_x11xx(self, api_mock):
        argv = ['basic', 'str', '--no-spaces', '--no-case', '--no-str']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 1,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_x21xx(self, api_mock):
        argv = ['basic', 'str', '--no-spaces', '--no-case', '--no-str', '--no-com']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 2,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_x31xx(self, api_mock):
        argv = ['basic', 'str', '--no-spaces', '--no-case', '--no-com']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 3,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_012xx(self, api_mock):
        argv = ['basic+numbers', 'str', '--no-spaces', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 2,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_014xx(self, api_mock):
        argv = ['bpe', '5k', 'str', '--no-spaces', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 4,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_015xx(self, api_mock):
        argv = ['bpe', '1k', 'str', '--no-spaces', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 5,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_xx6xx(self, api_mock):
        argv = ['bpe', '10k', 'str', '--no-spaces', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 6,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_xx8xx(self, api_mock):
        argv = ['chars', 'str', '--no-spaces', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 8,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_xx10x(self, api_mock):
        argv = ['basic', 'str', '--no-case']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 0,
            PrepParam.CAPS: 1
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    def test_parse_and_run_xx1x1(self, api_mock):
        argv = ['basic', 'str', '--no-spaces']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    @mock.patch('dataprep.cli.impl.Dataset')
    @mock.patch('dataprep.cli.impl.stages')
    @mock.patch('dataprep.cli.impl.os.getcwd')
    def test_parse_and_run_path(self, os_mock, stages_mock, dataset_mock, api_mock):
        os_mock.return_value='/path/to/curdir'
        dataset_mock.create = Mock(return_value=dataset_mock)
        argv = ['nosplit', '--path', '/path/to/dataset', '--no-spaces']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None, overriden_path_to_prep_dataset='/path/to/curdir')
        stages_mock.run_until_preprocessing.assert_called_with(dataset_mock, None)

    @mock.patch('dataprep.cli.impl.Dataset')
    @mock.patch('dataprep.cli.impl.stages')
    @mock.patch('dataprep.cli.impl.os.getcwd')
    def test_parse_and_run_path_short(self, os_mock, stages_mock, dataset_mock, api_mock):
        os_mock.return_value='/path/to/curdir'
        dataset_mock.create = Mock(return_value=dataset_mock)
        argv = ['nosplit', '-p', '/path/to/dataset', '--no-spaces']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None, overriden_path_to_prep_dataset='/path/to/curdir')
        stages_mock.run_until_preprocessing.assert_called_with(dataset_mock, None)

    @mock.patch('dataprep.cli.impl.Dataset')
    @mock.patch('dataprep.cli.impl.stages')
    def test_parse_and_run_output(self, stages_mock, dataset_mock, api_mock):
        dataset_mock.create = Mock(return_value=dataset_mock)
        argv = ['nosplit', '--path', '/path/to/dataset', '--output-path', '/path/to/output', '--no-spaces']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None, overriden_path_to_prep_dataset='/path/to/output')
        stages_mock.run_until_preprocessing.assert_called_with(dataset_mock, None)

    @mock.patch('dataprep.cli.impl.Dataset')
    @mock.patch('dataprep.cli.impl.stages')
    def test_parse_and_run_output_short(self, stages_mock, dataset_mock, api_mock):
        dataset_mock.create = Mock(return_value=dataset_mock)
        argv = ['nosplit', '--path', '/path/to/dataset', '-o', '/path/to/output', '--no-spaces']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None, overriden_path_to_prep_dataset='/path/to/output')
        stages_mock.run_until_preprocessing.assert_called_with(dataset_mock, None)

    def test_parse_and_run_text_with_output(self, api_mock):
        argv = ['nosplit', 'str', '-o', '/path/to/output', '--no-spaces']
        with self.assertRaises(DocoptExit) as context:
            parse_and_run(argv)

    def test_parse_and_run_all_short_config_options(self, api_mock):
        argv = ['basic', 'str', '-0lSCU']
        parse_and_run(argv)
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 3,
            PrepParam.COM_STR: 2,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        api_mock.preprocess.assert_called_with("str", prep_config, None)

    @mock.patch('dataprep.cli.impl.Dataset')
    @mock.patch('dataprep.cli.impl.bpe_learn')
    def test_parse_and_run_learnbpe_yes_false_java_yes(self, bpe_learn_mock, dataset_mock, api_mock):

        # given
        dataset_mock.create = Mock(return_value=dataset_mock)
        argv = ['learn-bpe', '1000', '-p', '/path/to/dataset', '--legacy']

        # when
        parse_and_run(argv)

        # then
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 0,
            PrepParam.CAPS: 0
        })
        bpe_config = BpeConfig({
            BpeParam.CASE: 'yes',
            BpeParam.WORD_END: False,
            BpeParam.BASE: 'java',
            BpeParam.UNICODE: 'yes',
        })
        dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, ['java'], None, bpe_config)
        bpe_learn_mock.run.assert_called_with(dataset_mock, 1000, bpe_config)

    @mock.patch('dataprep.cli.impl.Dataset')
    @mock.patch('dataprep.cli.impl.bpe_learn')
    def test_parse_and_run_learnbpe_no_true_code_no(self, bpe_learn_mock, dataset_mock, api_mock):

        # given
        dataset_mock.create = Mock(return_value=dataset_mock)
        argv = ['learn-bpe', '1000', '-p', '/path/to/dataset', '--no-case', '--no-unicode', '--word-end']

        # when
        parse_and_run(argv)

        # then
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 3,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 0,
            PrepParam.CAPS: 1
        })
        bpe_config = BpeConfig({
            BpeParam.CASE: 'no',
            BpeParam.WORD_END: True,
            BpeParam.BASE: 'code',
            BpeParam.UNICODE: 'no',
        })
        dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None, bpe_config)
        bpe_learn_mock.run.assert_called_with(dataset_mock, 1000, bpe_config)

    @mock.patch('dataprep.cli.impl.Dataset')
    @mock.patch('dataprep.cli.impl.bpe_learn')
    def test_parse_and_run_learnbpe_prefix_true_code_bytes(self, bpe_learn_mock, dataset_mock, api_mock):

        # given
        dataset_mock.create = Mock(return_value=dataset_mock)
        argv = ['learn-bpe', '1000', '-p', '/path/to/dataset', '--case-prefix', '--bytes', '--word-end']

        # when
        parse_and_run(argv)

        # then
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 0,
            PrepParam.CAPS: 0
        })
        bpe_config = BpeConfig({
            BpeParam.CASE: 'prefix',
            BpeParam.WORD_END: True,
            BpeParam.BASE: 'code',
            BpeParam.UNICODE: 'bytes',
        })
        dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None, bpe_config)
        bpe_learn_mock.run.assert_called_with(dataset_mock, 1000, bpe_config)


if __name__ == '__main__':
    unittest.main()
