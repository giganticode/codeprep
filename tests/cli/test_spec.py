from unittest import mock
from unittest.mock import Mock

import pytest
from docopt import DocoptExit

from dataprep.bpepkg.bpe_config import BpeConfig, BpeParam
from dataprep.cli.spec import parse_and_run
from dataprep.prepconfig import PrepParam, PrepConfig


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_uc100u(api_mock):
    argv = ['nosplit', 'str', '--no-spaces']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_Uc100u(api_mock):
    argv = ['nosplit', 'str', '--no-spaces', '--no-unicode']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


def test_xx0xxx_max_str_length():
    argv = ['nosplit', 'str', '--no-spaces', '--no-str', '--no-com', '--max-str-length=2']
    with pytest.raises(DocoptExit):
        parse_and_run(argv)

def test_xx0Fxx_max_str_length():
    argv = ['nosplit', 'str', '--no-spaces', '--no-str', '--no-com', '--full-strings']
    with pytest.raises(DocoptExit):
        parse_and_run(argv)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xxx0sx(api_mock):
    argv = ['nosplit', 'str']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xxxFsx(api_mock):
    argv = ['nosplit', 'str', '--full-strings']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xx2xxx_max_str_length0(api_mock):
    argv = ['nosplit', 'str', '--full-strings', '--max-str-length=0']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '2',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xx2xxx_max_str_length1(api_mock):
    argv = ['nosplit', 'str', '--full-strings', '--max-str-length=1']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '2',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xx2xxx(api_mock):
    argv = ['nosplit', 'str', '--full-strings', '--max-str-length=2']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '2',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xxExxx(api_mock):
    argv = ['nosplit', 'str', '--full-strings', '--max-str-length=14']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: 'E',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xx1xxx_max_str_length_large(api_mock):
    argv = ['nosplit', 'str', '--full-strings', '--max-str-length=999']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


def test_xxx0x1():
    argv = ['nosplit', 'str', '--no-spaces', '--no-case']
    with pytest.raises(DocoptExit) as context:
        parse_and_run(argv)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_uc110l(api_mock):
    argv = ['basic', 'str', '--no-spaces', '--no-case']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '1',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xxA1xx(api_mock):
    argv = ['basic', 'str', '--no-str', '--max-str-length=10']
    with pytest.raises(DocoptExit):
        parse_and_run(argv)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_Uxx1xx(api_mock):
    argv = ['basic', 'str', '--no-spaces', '--no-case', '--no-unicode']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '1',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xc01xx(api_mock):
    argv = ['basic', 'str', '--no-spaces', '--no-case', '--no-str']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '0',
        PrepParam.SPLIT: '1',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_x001xx(api_mock):
    argv = ['basic', 'str', '--no-spaces', '--no-case', '--no-str', '--no-com']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: '0',
        PrepParam.STR: '0',
        PrepParam.SPLIT: '1',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_x011xx(api_mock):
    argv = ['basic', 'str', '--no-spaces', '--no-case', '--no-com']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: '0',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '1',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_uc12xx(api_mock):
    argv = ['basic', 'str', '--no-spaces', '--no-case', '--split-numbers']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '2',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_uc13xx(api_mock):
    argv = ['basic', 'str', '--no-spaces', '--ronin']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '3',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


def test_xx0xxx_with_max_str_length():
    argv = ['basic', 'str', '--no-str', '--max-str-length=10']
    with pytest.raises(DocoptExit):
        parse_and_run(argv)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xxx3xl(api_mock):
    argv = ['basic', 'str', '--no-spaces', '--no-case', '--ronin']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '3',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_uc1sxx(api_mock):
    argv = ['basic', 'str', '--no-spaces', '--stem']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: 's',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_uc14xx(api_mock):
    argv = ['bpe', '5k', 'str', '--no-spaces']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '4',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, '5k')


def test_xxA4xx():
    argv = ['bpe', '5k', 'str', '--no-str', '--max-str-length=10']
    with pytest.raises(DocoptExit):
        parse_and_run(argv)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_uc15xx(api_mock):
    argv = ['bpe', '1k', 'str', '--no-spaces']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '5',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, '1k')


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xxx6xx(api_mock):
    argv = ['bpe', '10k', 'str', '--no-spaces']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '6',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, '10k')


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xxx9xx(api_mock):
    argv = ['bpe', 'custom-id-5000', 'str', '--no-spaces']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '9',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, 'custom-id-5000')


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xxx8xx(api_mock):
    argv = ['chars', 'str', '--no-spaces']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '8',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, '0')


def test_xxA8xx():
    argv = ['chars', 'str', '--no-str', '--max-str-length=10']
    with pytest.raises(DocoptExit):
        parse_and_run(argv)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xxx1sx(api_mock):
    argv = ['basic', 'str', '--no-case']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '1',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'l'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_xxx1xu(api_mock):
    argv = ['basic', 'str', '--no-spaces']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '1',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_path(api_mock):
    argv = ['nosplit', '--path', '/path/to/dataset', '--no-spaces']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.corpus.preprocess_corpus.assert_called_with('/path/to/dataset', prep_config, None, calc_vocab=False, extensions=None, output_path=None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_path_short(api_mock):
    argv = ['nosplit', '-p', '/path/to/dataset', '--no-spaces']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.corpus.preprocess_corpus.assert_called_with('/path/to/dataset', prep_config, None, calc_vocab=False,
                                                         extensions=None, output_path=None)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_output_and_vocab(api_mock):
    argv = ['nosplit', '--path', '/path/to/dataset', '--output-path', '/path/to/output', '--no-spaces', '--calc-vocab']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.corpus.preprocess_corpus.assert_called_with('/path/to/dataset', prep_config, None,
                                                         calc_vocab=True, extensions=None, output_path='/path/to/output')


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_output_and_vocab_short(api_mock):
    argv = ['nosplit', '--path', '/path/to/dataset', '-o', '/path/to/output', '--no-spaces', '-V']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })
    api_mock.corpus.preprocess_corpus.assert_called_with('/path/to/dataset', prep_config, None,
                                                         calc_vocab=True, extensions=None, output_path='/path/to/output')


def test_output_with_text():
    argv = ['nosplit', 'str', '-o', '/path/to/output', '--no-spaces']
    with pytest.raises(DocoptExit) as context:
        parse_and_run(argv)


@mock.patch('dataprep.cli.impl.dataprep.api', autospec=True)
def test_all_short_config_options(api_mock):
    argv = ['basic', 'str', '-0lSCU']
    parse_and_run(argv)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: '0',
        PrepParam.STR: '0',
        PrepParam.SPLIT: '1',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })
    api_mock.text.preprocess.assert_called_with("str", prep_config, None)


@mock.patch('dataprep.cli.impl.Dataset', autospec=True)
@mock.patch('dataprep.cli.impl.bpelearner', autospec=True)
def test_yes_false_java_yes(bpe_learner_mock, dataset_mock):

    # given
    dataset_mock.create = Mock(spec=dataset_mock, return_value=dataset_mock)
    argv = ['learn-bpe', '1000', '-p', '/path/to/dataset', '--legacy']

    # when
    parse_and_run(argv)

    # then
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: '0',
        PrepParam.STR: 'E',
        PrepParam.SPLIT: 'F',
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


@mock.patch('dataprep.cli.impl.Dataset', autospec=True)
@mock.patch('dataprep.cli.impl.bpelearner', autospec=True)
def test_no_true_code_no(bpe_learner_mock, dataset_mock):

    # given
    dataset_mock.create = Mock(spec=dataset_mock, return_value=dataset_mock)
    argv = ['learn-bpe', '1000', '-p', '/path/to/dataset', '--no-unicode', '--word-end']

    # when
    parse_and_run(argv)

    # then
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: '0',
        PrepParam.STR: 'E',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })
    bpe_config = BpeConfig({
        BpeParam.CASE: 'yes',
        BpeParam.WORD_END: True,
        BpeParam.BASE: 'code',
        BpeParam.UNICODE: 'no',
    })
    dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None, bpe_config)
    bpe_learner_mock.run.assert_called_with(dataset_mock, 1000, bpe_config)


@mock.patch('dataprep.cli.impl.Dataset', autospec=True)
@mock.patch('dataprep.cli.impl.bpelearner', autospec=True)
def test_true_true_code_bytes(bpe_learner_mock, dataset_mock):

    # given
    dataset_mock.create = Mock(spec=dataset_mock, return_value=dataset_mock)
    argv = ['learn-bpe', '1000', '-p', '/path/to/dataset', '--bytes', '--word-end']

    # when
    parse_and_run(argv)

    # then
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: '0',
        PrepParam.STR: 'E',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })
    bpe_config = BpeConfig({
        BpeParam.CASE: 'yes',
        BpeParam.WORD_END: True,
        BpeParam.BASE: 'code',
        BpeParam.UNICODE: 'bytes',
    })
    dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None, bpe_config)
    bpe_learner_mock.run.assert_called_with(dataset_mock, 1000, bpe_config)