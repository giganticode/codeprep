import os

from dataprep import api
from dataprep.api import create_prep_config_from_args
from dataprep.dataset import Dataset
from dataprep.cli import stages


def handle_splitting(args):
    prep_config =  create_prep_config_from_args(args)
    if args['<text>']:
        prep_text = api.preprocess(args['<text>'], prep_config)
        print(prep_text)
    else:
        path = os.path.abspath(args['--path'])
        output_path = args['--output-path'] if args['--output-path'] else '' #TODO this is bad. Fix it
        extension = 'java'
        dataset = Dataset.create(path, prep_config, extension, overriden_path_to_prep_dataset=output_path)
        stages.run_until_preprocessing(dataset)
        print(f"Preprocessed dataset is ready at {dataset.preprocessed.path}")
