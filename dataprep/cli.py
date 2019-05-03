import logging
import os
import sys

from dataprep import api
from dataprep.api import create_prep_config_from_args
from dataprep.config import app_name, version
from dataprep.dataset import Dataset

import docopt_subcommands as dsc

from dataprep import stages

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
    """usage: {program} bpe (1k | 5k | 10k) (-p <path> [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--no-case]

    Preprocess the dataset by splitting compound identifiers according to CamelCase and snake_case conventions,
    and apply byte-pair encoding (BPE) on top.

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


def handle_splitting(args):
    prep_config =  create_prep_config_from_args(args)
    if args['<text>']:
        prep_text = api.preprocess(args['<text>'], prep_config)
        print(prep_text)
    else:
        path = os.path.abspath(args['--path'])
        output_path = args['--output-path'] if args['--output-path'] else '' #TODO this is bad. Fix it
        extension = 'java' # This will be configurable in version 1.0.x
        dataset = Dataset.create(path, prep_config, extension, overriden_path_to_prep_dataset=output_path)
        stages.run_all(dataset)


def parse_and_run(args=sys.argv):
    logging.root.setLevel(logging.ERROR)
    dsc.main(app_name, f'{app_name} {version}', argv=args, exit_at_end=False)


if __name__ == '__main__':
    parse_and_run(['bpe', '1k', 'home/hgf'])