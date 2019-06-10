import logging
import os
from typing import Dict

from dataprep import api
from dataprep.api import create_prep_config_from_args
from dataprep.dataset import Dataset
from dataprep.cli import stages


def set_log_level(args: Dict[str, str]) -> None:
    if args['--verbose']:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.ERROR)


def handle_splitting(args):
    set_log_level(args)
    prep_config =  create_prep_config_from_args(args)
    if args['<text>']:
        prep_text = api.preprocess(args['<text>'], prep_config)
        print(prep_text)
    else:
        path = os.path.abspath(args['--path'])
        output_path = args['--output-path'] if args['--output-path'] else os.getcwd()
        extension = 'java'
        dataset = Dataset.create(path, prep_config, extension, overriden_path_to_prep_dataset=output_path)
        stages.run_until_preprocessing(dataset)
        print(f"Preprocessed dataset is ready at {dataset.preprocessed.path}")
