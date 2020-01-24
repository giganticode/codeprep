# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from unittest import mock

from unittest.mock import MagicMock

import pytest
from pytest import fixture

import codeprep
from codeprep.bpepkg import merge
from codeprep.bpepkg.merge import MergeList, Merge


@fixture
def file_handle_mock(mocker):
    mocker.patch('codeprep.bpepkg.merge.open')
    codeprep.bpepkg.merge.open.return_value = MagicMock(spec=['__enter__', '__exit__'])
    handle = codeprep.bpepkg.merge.open.return_value.__enter__.return_value
    return handle


def test_read_merges(file_handle_mock):
    file_handle_mock.__iter__.return_value = iter(['a b 67', 'b c 34', 'c d 94'])

    actual = merge.read_merges('file', 2)
    expected = MergeList().append(Merge(('a', 'b'), 67, 0)).append(Merge(('b', 'c'), 34, 1))

    assert expected == actual


def test_read_merges_with_wrong_delimiter(file_handle_mock):
    with pytest.raises(ValueError):
        file_handle_mock.__iter__.return_value = iter(['a\tb\t67'])

        merge.read_merges('file')


def test_dump_merges(file_handle_mock):
    merges = MergeList().append(Merge(('a', 'b'), 67, 0)).append(Merge(('b', 'c'), 34, 1))
    merge.dump_merges(merges, 'file')

    file_handle_mock.write.assert_has_calls([
        mock.call('a b 67\n'),
        mock.call('b c 34\n')
    ])