import logging

import docopt_subcommands as dsc

from dataprep.cli.impl import handle_splitting, handle_learnbpe
from dataprep.config import app_name, version

logger = logging.getLogger(__name__)


@dsc.command()
def nosplit_handler(args):
    """usage: {program} nosplit (-p <path> [-e <ext>] [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--calc-vocab] [--verbose]

    Preprocesses the dataset without splitting compound identifier.

    Options:
      -p, --path <path>                            Path to the dataset to be preprocessed.
      -e --ext <ext>                               Limits the set of input files to the files with the specified extension(s).
                                                   The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.
      -o <path-out>, --output-path <path-out>      Directory to which the pre-preprocessed corpus is to be written. If not specified, equals to '<path>_preprocessed'.
      <text>                                       Text to be preprocessed.

      --no-str, -S                                  Replace strings with <string> placeholders.
      --no-com, -C                                  Replace comments with <comment> placeholders.
      --no-spaces, -0                               Preserve newlines and tabs.
      --no-unicode, -U                              Replace words containing non-ascii characters with <non-en> placeholders.

      --calc-vocab -V                               Calculate vocabulary of the preprocessed dataset afterwards

      --verbose, -v                                 Print logs with log level DEBUG and higher to stdout.
    """
    handle_splitting(args)


@dsc.command()
def ronin_handler(args):
    """usage: {program} ronin (-p <path> [-e <ext>] [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--calc-vocab] [--verbose]

    Preprocesses the dataset splitting identifiers with Ronin algorithm: http://joss.theoj.org/papers/10.21105/joss.00653.
    Numbers are split into digits.

    Options:
      -p, --path <path>                            Path to the dataset to be preprocessed.
      -e --ext <ext>                               Limits the set of input files to the files with the specified extension(s).
                                                   The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.
      -o <path-out>, --output-path <path-out>      Directory to which the pre-preprocessed corpus is to be written. If not specified, equals to '<path>_preprocessed'.
      <text>                                       Text to be preprocessed.

      --no-str, -S                                  Replace strings with <string> placeholders.
      --no-com, -C                                  Replace comments with <comment> placeholders.
      --no-spaces, -0                               Preserve newlines and tabs.
      --no-unicode, -U                              Replace words containing non-ascii characters with <non-en> placeholders.

      --calc-vocab -V                               Calculate vocabulary of the preprocessed dataset afterwards

      --verbose, -v                                 Print logs with log level DEBUG and higher to stdout.
    """
    handle_splitting(args)


@dsc.command()
def chars_handler(args):
    """usage: {program} chars (-p <path> [-e <ext>] [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--no-case] [--calc-vocab] [--verbose]

    Preprocesses the dataset by splitting identifiers into characters.

    Options:
      -p, --path <path>                            Path to the dataset to be preprocessed.
      -e --ext <ext>                               Limits the set of input files to the files with the specified extension(s).
                                                   The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.
      -o <path-out>, --output-path <path-out>      Directory to which the pre-preprocessed corpus is to be written. If not specified, equals to '<path>_preprocessed'.
      <text>                                       Text to be preprocessed.

      --no-str, -S                                  Replace strings with <string> placeholders.
      --no-com, -C                                  Replace comments with <comment> placeholders.
      --no-spaces, -0                               Preserve newlines and tabs.
      --no-unicode, -U                              Replace words containing non-ascii characters with <non-en> placeholders.
      --no-case, -l                                 Lowercase words and encode information about case in <Cap> <CAP> tokens.

      --calc-vocab -V                               Calculate vocabulary of the preprocessed dataset afterwards

      --verbose, -v                                 Print logs with log level DEBUG and higher to stdout.
    """
    handle_splitting(args)


@dsc.command()
def basic_handler(args):
    """usage: {program} basic (-p <path> [-e <ext>] [-o <path-out>] | <text>) [-n [-s]] [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--no-case] [--calc-vocab] [--verbose]

    Preprocesses the dataset by splitting compound identifiers according to CamelCase and snake_case conventions.

    Options:
      -p, --path <path>                            Path to the dataset to be preprocessed.
      -e --ext <ext>                               Limits the set of input files to the files with the specified extension(s).
                                                   The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.
      -o <path-out>, --output-path <path-out>      Directory to which the pre-preprocessed corpus is to be written. If not specified, equals to '<path>_preprocessed'.
      <text>                                       Text to be preprocessed.

      --split-numbers, -n                           Split numbers into digits
      --stem, -s                                    Do stemming with Porter stemmer

      --no-str, -S                                  Replace strings with <string> placeholders.
      --no-com, -C                                  Replace comments with <comment> placeholders.
      --no-spaces, -0                               Preserve newlines and tabs.
      --no-unicode, -U                              Replace words containing non-ascii characters with <non-en> placeholders.
      --no-case, -l                                 Lowercase words and encode information about case in <Cap> <CAP> tokens.

      --calc-vocab -V                               Calculate vocabulary of the preprocessed dataset afterwards

      --verbose, -v                                 Print logs with log level DEBUG and higher to stdout.
    """
    handle_splitting(args)


@dsc.command()
def bpe_handler(args):
    """usage: {program} bpe (1k | 5k | 10k | <bpe-codes-id>) (-p <path> [-e <ext>] [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--no-case] [--calc-vocab] [--verbose]

    Preprocesses the dataset by splitting compound identifiers according to CamelCase and snake_case conventions,
    and applies byte-pair encoding (BPE) on top.

    Options:
      <bpe-codes-id>                               Id which defines bpe codes to use (1k, 5k, 10k are predefined ids)
      -p, --path <path>                            Path to the dataset to be preprocessed.
      -e --ext <ext>                               Limits the set of input files to the files with the specified extension(s).
                                                   The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.
      -o <path-out>, --output-path <path-out>      Directory to which the pre-preprocessed corpus is to be written. If not specified, equals to '<path>_preprocessed'.
      <text>                                       Text to be preprocessed.

      --no-str, -S                                  Replace strings with <string> placeholders.
      --no-com, -C                                  Replace comments with <comment> placeholders.
      --no-spaces, -0                               Preserve newlines and tabs.
      --no-unicode, -U                              Replace words containing non-ascii characters with <non-en> placeholders.
      --no-case, -l                                 Lowercase words and encode information about case in <Cap> <CAP> tokens.

      --calc-vocab -V                               Calculate vocabulary of the preprocessed dataset afterwards

      --verbose, -v                                 Print logs with log level DEBUG and higher to stdout.
    """
    handle_splitting(args)


@dsc.command()
def bpelearn_handler(args):
    """usage: {program} learn-bpe <n-merges> -p <path> [-e <ext>] [--id <bpe-codes-id>] [--no-case | --case-prefix] [--no-unicode | --bytes] [--word-end] [--legacy] [--verbose]

    Trains bpe codes on a specified corpus.

    Options:
      <n-merges>                                   The number of BPE merges to compute
      -p, --path <path>                            Path to the dataset to be used to learn bpe codes.
      -e --ext <ext>                               Limits the set of input files to the files with the specified extension(s).
                                                   The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.
      --id <bpe-codes-id>                          Give an id to bpe-codes. If not specified, will be assigned automatically based on the name of the directory bpe codes were learned from
      --no-case, -l                                Lowercase all the words before running bpe.
      --case-prefix, -c                            Let bpe algorithm decide whether case should a part of the word or not.
      --no-unicode, -U                             Ignore words containing non-ascii characters.
      --bytes, -b                                  Treat non-ascii characters as 2 bytes and do real byte-pair encoding.
      --word-end, -z                               Add a special character to the end of each word.
      --legacy                                     Parse using legacy parser (only files with extension “.java” will be processed)
      --verbose, -v                                Print logs with log level DEBUG and higher to stdout.
    """
    handle_learnbpe(args)


def parse_and_run(args):
    dsc.main(app_name, f'{app_name} {version}', argv=args, exit_at_end=False)
