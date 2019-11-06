from unittest import mock
from unittest.mock import Mock

from dataprep.api.corpus import preprocess_corpus
from dataprep.prepconfig import PrepConfig, PrepParam


@mock.patch('dataprep.api.corpus.Dataset', autospec=True)
@mock.patch('dataprep.api.corpus.stages', autospec=True)
@mock.patch('dataprep.cli.impl.os.getcwd', autospec=True, return_value='/path/to/curdir')
def test_simple(os_mock, stages_mock, dataset_mock):
    # given
    dataset_mock.create = Mock(spec=dataset_mock, return_value=dataset_mock)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u',
    })

    # when
    preprocess_corpus('/path/to/dataset', prep_config)

    # then
    dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None,
                                           overriden_path_to_prep_dataset='/path/to/curdir')
    stages_mock.run_until_preprocessing.assert_called_with(dataset_mock, None)


@mock.patch('dataprep.api.corpus.Dataset', autospec=True)
@mock.patch('dataprep.api.corpus.stages', autospec=True)
@mock.patch('dataprep.cli.impl.os.getcwd', autospec=True, return_value='/path/to/curdir')
def test_calc_vocab(os_mock, stages_mock, dataset_mock):
    # given
    dataset_mock.create = Mock(spec=dataset_mock, return_value=dataset_mock)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u',
    })

    # when
    preprocess_corpus('/path/to/dataset', prep_config, calc_vocab=True)

    # then
    dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None,
                                           overriden_path_to_prep_dataset='/path/to/curdir')
    stages_mock.run_until_vocab.assert_called_with(dataset_mock, None)


@mock.patch('dataprep.api.corpus.Dataset', autospec=True)
@mock.patch('dataprep.api.corpus.stages', autospec=True)
def test_output(stages_mock, dataset_mock):
    # given
    dataset_mock.create = Mock(spec=dataset_mock, return_value=dataset_mock)
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u',
    })

    # when
    preprocess_corpus('/path/to/dataset', prep_config, output_path='/path/to/output')

    # then
    dataset_mock.create.assert_called_with('/path/to/dataset', prep_config, None, None,
                                           overriden_path_to_prep_dataset='/path/to/output')
    stages_mock.run_until_preprocessing.assert_called_with(dataset_mock, None)
