"""Dataprep.

Usage:
  dataprep (-p <path> [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] nosplit
  dataprep (-p <path> [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--no-case] chars
  dataprep (-p <path> [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--no-case] basic
  dataprep (-p <path> [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--no-case] basic+numbers
  dataprep (-p <path> [-o <path-out>] | <text>) [--no-str] [--no-com] [--no-spaces] [--no-unicode] [--no-case] bpe (1k | 5k | 10k)
  dataprep (-h | --help)
  dataprep --version

Options:
   -h, --help                                   Show this screen.
  --version                                     Show version.

   <text>                                       Text to be preprocessed.
   -p <path>, --path <path>                     Path to the dataset to be preprocessed.
   -o <path-out>, --output-path <path-out>      Directory to which the pre-preprocessed corpus is to be written. If not specified, equals to '<path>_preprocessed'

  --no-str, -S                                  Replace strings with <string> placeholders.
  --no-com, -C                                  Replace comments with <comment> placeholders.
  --no-spaces, -0                               Preserve newlines and tabs.
  --no-unicode, -U                              Replace words containing non-ascii characters with <non-en> placeholders.
  --no-case, -l                                 Lowercase words and encode information about case in <Cap> <CAP> tokens.
"""
import logging
import os
import sys

from docopt import docopt

from dataprep import parse_projects, api, to_repr
from dataprep.api import create_prep_config_from_args
from dataprep.config import version, app_name

logger = logging.getLogger(__name__)


def parse_run_options(arguments):
    return arguments


def parse_command_line(argv):
    arguments = docopt(__doc__, argv, version=f'{app_name} {version}')
    return create_prep_config_from_args(arguments), parse_run_options(arguments)


def run(argv):
    logging.root.setLevel(logging.ERROR)
    prep_config, run_options = parse_command_line(argv)
    if run_options['<text>']:
        prep_text = api.preprocess(run_options['<text>'], prep_config)
        print(prep_text)
    else:
        full_path_to_dataset = os.path.abspath(run_options['--path'])
        output_path = run_options['--output-path'] if run_options['--output-path'] else f'{full_path_to_dataset}_preprocessed_{prep_config}'
        if os.path.exists(output_path):
            logger.error(f"Output path already exists: {output_path}")
            exit(23)
        print("Stage 1/2: Parsing...")
        parse_projects.run(full_path_to_dataset)
        print("Stage 2/2. Preprocessing...")
        to_repr.run(os.path.basename(full_path_to_dataset), prep_config, output_path)
        print(f"The output is ready at {os.path.abspath(output_path)}")


def main():
    run(sys.argv[1:])


if __name__ == '__main__':
    main()
