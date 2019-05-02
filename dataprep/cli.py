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
   -o <path-out>, --output-path <path-out>      Directory to which the pre-preprocessed corpus is to be written. If not specified, equals to '<path>_preprocessed'.

  --no-str, -S                                  Replace strings with <string> placeholders.
  --no-com, -C                                  Replace comments with <comment> placeholders.
  --no-spaces, -0                               Preserve newlines and tabs.
  --no-unicode, -U                              Replace words containing non-ascii characters with <non-en> placeholders.
  --no-case, -l                                 Lowercase words and encode information about case in <Cap> <CAP> tokens.
"""
import logging
import os

from docopt import docopt

from dataprep import api, parse_projects, to_repr
from dataprep.api import create_prep_config_from_args
from dataprep.config import app_name, version
from dataprep.dataset import Dataset

logger = logging.getLogger(__name__)


def parse_command_line(argv):
    run_options = docopt(__doc__, argv, version=f'{app_name} {version}')

    return create_prep_config_from_args(run_options), run_options


def run_parsing(dataset):
    if not dataset.parsed.ready():
        parse_projects.run(dataset)
    elif not dataset.parsed.is_up_to_date():
        dataset.parsed.archive()
        parse_projects.run(dataset)
    else:
        print("Parsed dataset is up-to-date.")


def run_preprocessing(dataset):
    print("Stage 1/2: Parsing...")
    run_parsing(dataset)
    print("Stage 2/2. Preprocessing...")
    to_repr.run(dataset)


def run(argv):
    logging.root.setLevel(logging.ERROR)
    prep_config, run_options = parse_command_line(argv)
    if run_options['<text>']:
        prep_text = api.preprocess(run_options['<text>'], prep_config)
        print(prep_text)
    else:
        path = os.path.abspath(run_options['--path'])
        output_path = run_options['--output-path'] if run_options['--output-path'] else '' #TODO this is bad. Fix it
        extension = 'java' # This will be configurable in version 1.0.x
        dataset = Dataset.create(path, prep_config, extension, overriden_path_to_prep_dataset=output_path)

        if not dataset.preprocessed.ready():
            run_preprocessing(dataset)
        elif dataset.preprocessed.is_up_to_date():
            print(f"Dataset is already preprocessed at: {dataset.preprocessed.path}")
            exit(0)
        else:
            dataset.preprocessed.archive()
            run_preprocessing(dataset)
        print(f"The preprocessed dataset is at {dataset.preprocessed.path}")