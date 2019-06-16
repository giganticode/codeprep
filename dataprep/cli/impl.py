import logging
import os

from typing import Dict, List

from dataprep import api
from dataprep.api import create_prep_config_from_args
from dataprep.bpepkg import bpe_learn
from dataprep.bpepkg.bpe_config import BpeParam, BpeConfig
from dataprep.bpepkg.bperegistry import InvalidBpeCodesIdError, CustomBpeConfig
from dataprep.cli import stages
from dataprep.dataset import Dataset


def set_log_level(args: Dict[str, str]) -> None:
    if args['--verbose']:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.ERROR)


def handle_learnbpe(args):
    set_log_level(args)
    path = os.path.abspath(args['--path'])
    bpe_config = create_bpe_config_from_args(args)
    n_merges = int(args['<n-merges>'])
    parsed_extensions = parse_extension_pattern(args['--ext']) if args['--ext'] else None
    if args['--legacy']:
        if parsed_extensions and parsed_extensions != ['java']:
            print("Only --ext 'java' is supported when --legacy is specified")
            return
        else:
            extensions = ['java']
    else:
        extensions = parsed_extensions
    bpe_codes_id = args['--id']
    dataset = Dataset.create(path, bpe_config.to_prep_config(), extensions, None, bpe_config)

    if not dataset.bpe_codes_id:
        dataset.assign_bpe_codes_id(bpe_config, predefined_bpe_codes_id=bpe_codes_id)
    elif bpe_codes_id:
        print(f"Ignoring passed bpe codes id: {bpe_codes_id}. "
              f"This dataset has already been assigned id: {dataset.bpe_codes_id}")

    bpe_learn.run(dataset, n_merges, bpe_config)


def parse_extension_pattern(extension_pattern: str) -> List[str]:
    return extension_pattern.split("|")


def handle_splitting(args):
    set_log_level(args)
    try:
        prep_config = create_prep_config_from_args(args)
        bpe_codes_id = args['<bpe-codes-id>'] if '<bpe-codes-id>' in args else None
        if args['<text>']:
            prep_text = api.preprocess(args['<text>'], prep_config, bpe_codes_id)
            print(prep_text)
        else:
            path = os.path.abspath(args['--path'])
            output_path = args['--output-path'] if args['--output-path'] else os.getcwd()
            extensions = parse_extension_pattern(args['--ext']) if args['--ext'] else None
            custom_bpe_config = CustomBpeConfig.from_id(bpe_codes_id) if bpe_codes_id else None
            dataset = Dataset.create(path, prep_config, extensions, custom_bpe_config, overriden_path_to_prep_dataset=output_path)
            stages.run_until_preprocessing(dataset, custom_bpe_config)
            print(f"Preprocessed dataset is ready at {dataset.preprocessed.path}")
    except InvalidBpeCodesIdError as err:
        print(err)
        return


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
        BpeParam.BASE: 'java' if run_options['--legacy'] else 'code',
        BpeParam.UNICODE: unicode
    })