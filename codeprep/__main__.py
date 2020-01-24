# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys

from codeprep.cli.spec import parse_and_run


def main():
    parse_and_run(sys.argv[1:])


if __name__ == '__main__':
    import codeprep.api.text as api
    print(api.basic("hxwdwefwfwi"))