import os

from typing import Dict

from dataprep import api
from dataprep.api import create_prep_config_from_args
from dataprep.bperegistry import create_custom_bpe_config, InvalidBpeCodesIdError
from dataprep.dataset import Dataset
from dataprep.cli import stages
from dataprep.split import bpe_learn
from dataprep.split.bpe_config import BpeParam, BpeConfig


def handle_learnbpe(args):
    path = os.path.abspath(args['--path'])
    bpe_config = create_bpe_config_from_args(args)
    n_merges = int(args['<n-merges>'])
    extension = 'java' if args['java'] else None
    bpe_codes_id = args['--id']
    dataset = Dataset.create(path, bpe_config.to_prep_config(), extension, None, bpe_config)

    if not dataset.bpe_codes_id:
        dataset.assign_bpe_codes_id(predefined_bpe_codes_id=bpe_codes_id)
    elif bpe_codes_id:
        print(f"Ignoring passed bpe codes id: {bpe_codes_id}. "
              f"This dataset has already been assigned id: {dataset.bpe_codes_id}")

    bpe_learn.run(dataset, n_merges, bpe_config=bpe_config, extension=extension)


def handle_splitting(args):
    try:
        prep_config = create_prep_config_from_args(args)
        bpe_codes_id = args['<bpe-codes-id>'] if '<bpe-codes-id>' in args else None
        if args['<text>']:
            prep_text = api.preprocess(args['<text>'], prep_config, bpe_codes_id)
            print(prep_text)
        else:
            path = os.path.abspath(args['--path'])
            output_path = args['--output-path'] if args['--output-path'] else '' #TODO this is bad. Fix it
            extension = 'java'
            custom_bpe_config = create_custom_bpe_config(bpe_codes_id) if bpe_codes_id else None
            dataset = Dataset.create(path, prep_config, extension, custom_bpe_config, overriden_path_to_prep_dataset=output_path)
            stages.run_until_preprocessing(dataset, custom_bpe_config)
            print(f"Preprocessed dataset is ready at {dataset.preprocessed.path}")
    except InvalidBpeCodesIdError as err:
        print(err)
        return


def get_bpe_param_base_value(run_options):
    if run_options["code"]:
        return "code"
    elif run_options["java"]:
        return "java"
    else:
        raise AssertionError()


def create_bpe_config_from_args(run_options: Dict[str, str]) -> BpeConfig:
    if run_options['--no-case']:
        case = 'no'
    elif run_options['--case-prefix']:
        case = 'prefix'
    else:
        case = 'yes'
    if run_options['--no-unicode']:
        unicode = 'no'
    elif run_options['--bytes']:
        unicode = 'bytes'
    else:
        unicode = 'yes'
    return BpeConfig({
        BpeParam.CASE: case,
        BpeParam.WORD_END: run_options["--word-end"],
        BpeParam.BASE: get_bpe_param_base_value(run_options),
        BpeParam.UNICODE: unicode
    })