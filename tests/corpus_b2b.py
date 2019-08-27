import os
import unittest
from unittest import mock

import docopt_subcommands as dsc

from dataprep.bpepkg.bpe_encode import BpeData
from dataprep.bpepkg.merge import read_merges
from dataprep.cli.spec import parse_and_run
from dataprep.fileutils import read_file_contents
from dataprep.parse.core import convert_text
from dataprep.prepconfig import PrepConfig, PrepParam
from dataprep.to_repr import to_repr

#TODO use relative path
TEST_FILE = b"C:\\Users\Home\dev\dataprep\\test-resources\AppXMark.java"

#TODO make test file small and measure time of excution

# class BpePerformanceTest(unittest.TestCase):
#     def test(self):
#         prep_config = PrepConfig({
#             PrepParam.EN_ONLY: 'u',
#             PrepParam.COM: 'c',
#             PrepParam.STR: '1',
#             PrepParam.SPLIT: '9',
#             PrepParam.TABS_NEWLINES: 's',
#             PrepParam.CASE: 'u'
#         })
#
#         bpe_data = BpeData(merges_cache=[],
#                            merges = read_merges('C:\\Users\Home\dev\dataprep\dataprep\data\\bpe\\10k\merges.txt', 1000))
#
#         lines_from_file, path = read_file_contents(TEST_FILE)
#         extension_bin = os.path.splitext(TEST_FILE)[1].decode()[1:]
#         parsed = [p for p in convert_text("\n".join(lines_from_file), extension_bin)]
#         repr, metadata = to_repr(prep_config, parsed, bpe_data)
