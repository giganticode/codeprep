# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import os
from unittest import mock
from unittest.mock import Mock

from codeprep.api.corpus import preprocess_corpus
from codeprep.prepconfig import PrepConfig, PrepParam

PATH_TO_CUR_DIR_STUB = os.path.join('path', 'to', 'curdir')
PATH_TO_DATASET_STUB = os.path.join('path', 'to', 'dataset')
PATH_TO_OUTPUT_STUB = os.path.join('path', 'to', 'output')


@mock.patch('codeprep.api.corpus.Dataset', autospec=True)
@mock.patch('codeprep.api.corpus.stages', autospec=True)
@mock.patch('codeprep.cli.impl.os.getcwd', autospec=True, return_value=PATH_TO_CUR_DIR_STUB)
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
    preprocess_corpus(PATH_TO_DATASET_STUB, prep_config)

    # then
    dataset_mock.create.assert_called_with(PATH_TO_DATASET_STUB, prep_config, None, None,
                                           overriden_path_to_prep_dataset=PATH_TO_CUR_DIR_STUB)
    stages_mock.run_until_preprocessing.assert_called_with(dataset_mock, None)


@mock.patch('codeprep.api.corpus.Dataset', autospec=True)
@mock.patch('codeprep.api.corpus.stages', autospec=True)
@mock.patch('codeprep.cli.impl.os.getcwd', autospec=True, return_value=PATH_TO_CUR_DIR_STUB)
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
    preprocess_corpus(PATH_TO_DATASET_STUB, prep_config, calc_vocab=True)

    # then
    dataset_mock.create.assert_called_with(PATH_TO_DATASET_STUB, prep_config, None, None,
                                           overriden_path_to_prep_dataset=PATH_TO_CUR_DIR_STUB)
    stages_mock.run_until_vocab.assert_called_with(dataset_mock, None)


@mock.patch('codeprep.api.corpus.Dataset', autospec=True)
@mock.patch('codeprep.api.corpus.stages', autospec=True)
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
    preprocess_corpus(PATH_TO_DATASET_STUB, prep_config, output_path=PATH_TO_OUTPUT_STUB)

    # then
    dataset_mock.create.assert_called_with(PATH_TO_DATASET_STUB, prep_config, None, None,
                                           overriden_path_to_prep_dataset=PATH_TO_OUTPUT_STUB)
    stages_mock.run_until_preprocessing.assert_called_with(dataset_mock, None)