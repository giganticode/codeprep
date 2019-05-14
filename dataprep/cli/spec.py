import logging

import docopt_subcommands as dsc

from dataprep.cli.impl import handle_splitting, handle_learnbpe
from dataprep.config import app_name, version

logger = logging.getLogger(__name__)


@dsc.command()
def nosplit_handler(args):
    """usage: {program} nosplit (-p <path> [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces]

    Preprocess the dataset without splitting compound identifier.

    Options:
      -p, --path <path>                            Path to the dataset to be preprocessed.
      -o <path-out>, --output-path <path-out>      Directory to which the pre-preprocessed corpus is to be written. If not specified, equals to '<path>_preprocessed'.
      <text>                                       Text to be preprocessed.

      --no-str, -S                                  Replace strings with <string> placeholders.
      --no-com, -C                                  Replace comments with <comment> placeholders.
      --no-spaces, -0                               Preserve newlines and tabs.
    """
    handle_splitting(args)


@dsc.command()
def chars_handler(args):
    """usage: {program} chars (-p <path> [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--no-case]

    Preprocess the dataset by splitting identifiers into characters.

    Options:
      -p, --path <path>                            Path to the dataset to be preprocessed.
      -o <path-out>, --output-path <path-out>      Directory to which the pre-preprocessed corpus is to be written. If not specified, equals to '<path>_preprocessed'.
      <text>                                       Text to be preprocessed.

      --no-str, -S                                  Replace strings with <string> placeholders.
      --no-com, -C                                  Replace comments with <comment> placeholders.
      --no-spaces, -0                               Preserve newlines and tabs.
      --no-unicode, -U                              Replace words containing non-ascii characters with <non-en> placeholders.
      --no-case, -l                                 Lowercase words and encode information about case in <Cap> <CAP> tokens.
    """
    handle_splitting(args)


@dsc.command()
def basic_handler(args):
    """usage: {program} basic (-p <path> [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--no-case]

    Preprocess the dataset by splitting compound identifiers according to CamelCase and snake_case conventions.

    Options:
      -p, --path <path>                            Path to the dataset to be preprocessed.
      -o <path-out>, --output-path <path-out>      Directory to which the pre-preprocessed corpus is to be written. If not specified, equals to '<path>_preprocessed'.
      <text>                                       Text to be preprocessed.

      --no-str, -S                                  Replace strings with <string> placeholders.
      --no-com, -C                                  Replace comments with <comment> placeholders.
      --no-spaces, -0                               Preserve newlines and tabs.
      --no-unicode, -U                              Replace words containing non-ascii characters with <non-en> placeholders.
      --no-case, -l                                 Lowercase words and encode information about case in <Cap> <CAP> tokens.
    """
    handle_splitting(args)


@dsc.command()
def basic_plus_numbers_handler(args):
    """usage: {program} basic+numbers (-p <path> [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--no-case]

    Preprocess the dataset by splitting compound identifiers according to CamelCase and snake_case conventions,
    and splitting numbers into digits.

    Options:
      -p, --path <path>                            Path to the dataset to be preprocessed.
      -o <path-out>, --output-path <path-out>      Directory to which the pre-preprocessed corpus is to be written. If not specified, equals to '<path>_preprocessed'.
      <text>                                       Text to be preprocessed.

      --no-str, -S                                  Replace strings with <string> placeholders.
      --no-com, -C                                  Replace comments with <comment> placeholders.
      --no-spaces, -0                               Preserve newlines and tabs.
      --no-unicode, -U                              Replace words containing non-ascii characters with <non-en> placeholders.
      --no-case, -l                                 Lowercase words and encode information about case in <Cap> <CAP> tokens.
    """
    handle_splitting(args)


@dsc.command()
def bpe_handler(args):
    """usage: {program} bpe (1k | 5k | 10k | <bpe-codes-id>) (-p <path> [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--no-case]

    Preprocess the dataset by splitting compound identifiers according to CamelCase and snake_case conventions,
    and apply byte-pair encoding (BPE) on top.

    Options:
      <bpe-codes-id>                               Id which defines bpe codes to use (1k, 5k, 10k are predefined ids)
      -p, --path <path>                            Path to the dataset to be preprocessed.
      -o <path-out>, --output-path <path-out>      Directory to which the pre-preprocessed corpus is to be written. If not specified, equals to '<path>_preprocessed'.
      <text>                                       Text to be preprocessed.

      --no-str, -S                                  Replace strings with <string> placeholders.
      --no-com, -C                                  Replace comments with <comment> placeholders.
      --no-spaces, -0                               Preserve newlines and tabs.
      --no-unicode, -U                              Replace words containing non-ascii characters with <non-en> placeholders.
      --no-case, -l                                 Lowercase words and encode information about case in <Cap> <CAP> tokens.
    """
    handle_splitting(args)


@dsc.command()
def bpelearn_handler(args):
    """usage: {program} learn-bpe (code | java) <n-merges> -p <path> [-o <path-out>] [--id <bpe-codes-id>] [--no-case | --case-prefix] [--no-unicode | --bytes] [--word-end]

    #TODO

    Options:
      code                                         Run bpe on all source code files.
      java                                         Run bpe only on java files.
      <n-merges>                                   The number of BPE merges to compute
      -p, --path <path>                            Path to the dataset to be used to learn bpe codes.
      -o <path-out>, --output-path <path-out>      Path to the file to which computed bpe codes are to be written. If not specified, equals to '<path>_bpe_codes.txt'.
      --id <bpe-codes-id>                          Give an id to bpe-codes. If not specified, will be assigned automatically based on the name of the directory bpe codes were learned from
      --no-case, -l                                Lowercase all the words before running bpe.
      --case-prefix, -c                            Let bpe algorithm decide whether case should a part of the word or not.
      --no-unicode, -U                             Ignore words containing non-ascii characters.
      --bytes, -b                                  Treat non-ascii characters as 2 bytes and do real byte-pair encoding.
      --word-end, -e                               Add a special character to the end of each word.
    """
    handle_learnbpe(args)


def parse_and_run(args):
    logging.root.setLevel(logging.ERROR)
    dsc.main(app_name, f'{app_name} {version}', argv=args, exit_at_end=False)
