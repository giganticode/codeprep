import logging
import os

from typing import Dict

import dataprep
from dataprep.api.corpus import parse_extension_pattern
from dataprep.api.common import create_split_value, create_com_str_value
from dataprep.bpepkg.bpe_config import BpeParam, BpeConfig
from dataprep.installation import bpelearner
from dataprep.installation.bperegistry import InvalidBpeCodesIdError
from dataprep.installation.dataset import Dataset
from dataprep.prepconfig import PrepConfig, PrepParam


def set_log_level(args: Dict[str, str]) -> None:
    if args['--verbose']:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.ERROR)


def is_option_true(args: Dict, option: str):
    return option in args and args[option]


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

    bpelearner.run(dataset, n_merges, bpe_config)


def handle_splitting(args: Dict) -> None:
    set_log_level(args)
    try:
        prep_config = create_prep_config_from_args(args)
        bpe_codes_id = args['<bpe-codes-id>'] if '<bpe-codes-id>' in args else None
        if args['<text>']:
            prep_text = dataprep.api.text.preprocess(args['<text>'], prep_config, bpe_codes_id)
            print(prep_text)
        else:
            dataprep.api.corpus.preprocess_corpus(args['--path'], prep_config, bpe_codes_id,
                                                  extensions=args['--ext'],
                                                  output_path=args['--output-path'],
                                                  calc_vocab=bool(args['--calc-vocab']))
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


def create_prep_config_from_args(arguments: Dict) -> PrepConfig:
    return PrepConfig({
        PrepParam.EN_ONLY: 'U' if is_option_true(arguments, '--no-unicode') else 'u',
        PrepParam.COM_STR: create_com_str_value_from_args(arguments),
        PrepParam.SPLIT: create_split_value_from_args(arguments),
        PrepParam.TABS_NEWLINES: '0' if arguments['--no-spaces'] else 's',
        PrepParam.CASE: 'l' if is_option_true(arguments, '--no-case') or is_option_true(arguments, '--stem') else 'u'
    })


def create_split_value_from_args(arguments: Dict) -> str:
    if is_option_true(arguments, 'nosplit'):
        return create_split_value('nosplit')
    elif is_option_true(arguments, 'chars'):
        return create_split_value('chars')
    elif is_option_true(arguments, 'ronin'):
        return create_split_value('ronin')
    elif is_option_true(arguments, 'basic'):
        return create_split_value('basic',
                                  stem=is_option_true(arguments, '--stem'),
                                  split_numbers=is_option_true(arguments, '--split-numbers'))
    elif is_option_true(arguments, 'bpe'):
        if arguments['1k']:
            return create_split_value('bpe', '1k')
        elif arguments['5k']:
            return create_split_value('bpe', '5k')
        elif arguments['10k']:
            return create_split_value('bpe', '10k')
        else:
            return create_split_value('bpe')
    else:
        raise AssertionError(f"Invalid split option: {arguments}")


def create_com_str_value_from_args(arguments: Dict) -> str:
    return create_com_str_value(no_com=arguments['--no-com'], no_str=arguments['--no-str'])