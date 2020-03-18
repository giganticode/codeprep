# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import os
import platform
import shutil

from codeprep.cli.spec import parse_and_run

import codeprep.api.corpus as api
from codeprep.config import root_package_dir

PATH_TO_TEST_CORPUS = os.path.join(root_package_dir, '..', 'test-data', 'test-corpus')
TEST_OUTPUT = os.path.join(root_package_dir, '..', 'test-output')


def test_preprocess_with_different_options():
    calc_vocab = platform.system() != 'Darwin'
    api.basic(path=PATH_TO_TEST_CORPUS, extensions="java", output_path=TEST_OUTPUT, calc_vocab=calc_vocab)
    api.basic(path=PATH_TO_TEST_CORPUS, extensions="java", split_numbers=True, ronin=True, stem=True,
              no_spaces=True, no_unicode=True, no_case=True, no_com=True, no_str=True, max_str_length=30,
              output_path=TEST_OUTPUT, calc_vocab=calc_vocab)
    api.chars(path=PATH_TO_TEST_CORPUS, extensions="java", output_path=TEST_OUTPUT, calc_vocab=calc_vocab)
    api.nosplit(path=PATH_TO_TEST_CORPUS, extensions="java", output_path=TEST_OUTPUT, calc_vocab=calc_vocab)
    api.bpe(path=PATH_TO_TEST_CORPUS, bpe_codes_id='10k', extensions="java", output_path=TEST_OUTPUT, calc_vocab=calc_vocab)


def test_learn_bpe_codes():
    if platform.system() != 'Darwin':
        parse_and_run(['learn-bpe', '100', '-p', PATH_TO_TEST_CORPUS, '-e', 'java'])
        parse_and_run(['learn-bpe', '150', '-p', PATH_TO_TEST_CORPUS, '-e', 'java'])

        api.bpe(path=PATH_TO_TEST_CORPUS, bpe_codes_id='test-corpus-130', extensions="java", output_path=TEST_OUTPUT)
    else:
        print('Skipping the test on OSx.')


def teardown_function(function):
    print(f'Removing the outputs at: {TEST_OUTPUT}')
    if os.path.exists(TEST_OUTPUT):
        shutil.rmtree(TEST_OUTPUT)
