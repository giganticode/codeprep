# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import importlib
from os.path import dirname, basename, isfile, join
import glob

modules = glob.glob(join(dirname(__file__), "*.py"))
for f in modules:
    if isfile(f) and not f.endswith('__init__.py'):
        importlib.import_module(f'{__package__}.{basename(f)[:-3]}')