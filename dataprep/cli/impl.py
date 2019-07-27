import logging
import os
import sys
from typing import Dict, Optional, Any

import dataprep
import dataprep.api.corpus
import dataprep.api.text
from dataprep.api.common import create_split_value, create_str_value
from dataprep.bpepkg.bpe_config import BpeParam, BpeConfig
from dataprep.infrastructure import bpelearner
from dataprep.infrastructure.bperegistry import InvalidBpeCodesIdError, USER_PREDEFINED_BPE_CODES
from dataprep.infrastructure.dataset import Dataset, normalize_extension_string
from dataprep.prepconfig import PrepConfig, PrepParam


logger = logging.getLogger(__name__)


def set_log_level(args: Dict[str, str]) -> None:
    if args['--verbose']:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.ERROR)


def get_option(args: Dict, option: str) -> Optional[Any]:
    return args[option] if option in args else None


def is_option_true(args: Dict, option: str) -> bool:
    return bool(get_option(args, option))


def handle_learnbpe(args):
    set_log_level(args)
    path = os.path.abspath(args['--path'])
    bpe_config = create_bpe_config_from_args(args)
    n_merges = int(args['<n-merges>'])
    if args['--legacy']:
        parsed_extensions = normalize_extension_string(args['--ext'])
        if parsed_extensions and parsed_extensions != ['java']:
            print("Only --ext 'java' is supported when --legacy is specified")
            return
        else:
            extensions = 'java'
    else:
        extensions = args['--ext']
    bpe_codes_id = args['--id']
    dataset = Dataset.create(path, bpe_config.to_prep_config(), extensions, None, bpe_config)

    if not dataset.bpe_codes_id:
        dataset.assign_bpe_codes_id(bpe_config, predefined_bpe_codes_id=bpe_codes_id)
    elif bpe_codes_id:
        logger.warning(f"Ignoring passed bpe codes id: {bpe_codes_id}. "
              f"This dataset has already been assigned id: {dataset.bpe_codes_id}")

    bpelearner.run(dataset, n_merges, bpe_config)


def handle_splitting(args: Dict) -> None:
    set_log_level(args)
    try:
        prep_config = create_prep_config_from_args(args)
        bpe_codes_id = get_option(args, '<bpe-codes-id>') or get_predefined_bpe_codes_id(args)
        if args['<text>']:
            prep_text = dataprep.api.text.preprocess(args['<text>'], prep_config, bpe_codes_id)
            print(prep_text)
        else:
            dataprep.api.corpus.preprocess_corpus(args['--path'], prep_config, bpe_codes_id,
                                                  extensions=args['--ext'],
                                                  output_path=args['--output-path'],
                                                  calc_vocab=bool(args['--calc-vocab']))
    except InvalidBpeCodesIdError as err:
        logger.error(err)
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
    max_str_length = get_option(arguments, '--max-str-length')
    max_str_length = int(max_str_length) if max_str_length is not None else sys.maxsize
    return PrepConfig({
        PrepParam.EN_ONLY: 'U' if is_option_true(arguments, '--no-unicode') else 'u',
        PrepParam.COM: '0' if is_option_true(arguments, '--no-com') else 'c',
        PrepParam.STR: create_str_value(is_option_true(arguments, '--no-str'), max_str_length),
        PrepParam.SPLIT: create_split_value_from_args(arguments),
        PrepParam.TABS_NEWLINES: '0' if is_option_true(arguments, '--no-spaces') else 's',
        PrepParam.CASE: 'l' if is_option_true(arguments, '--no-case') or is_option_true(arguments, '--stem') else 'u',
    })


def get_predefined_bpe_codes_id(arguments: Dict) -> Optional[str]:
    for predefined_id in USER_PREDEFINED_BPE_CODES:
        if is_option_true(arguments, predefined_id):
            return predefined_id

    return None


def create_split_value_from_args(arguments: Dict) -> str:
    if is_option_true(arguments, 'nosplit'):
        return create_split_value('nosplit', full_strings=is_option_true(arguments, '--full-strings'))
    elif is_option_true(arguments, 'chars'):
        return create_split_value('chars')
    elif is_option_true(arguments, 'basic'):
        return create_split_value('basic',
                                  split_numbers=is_option_true(arguments, '--split-numbers'),
                                  ronin=is_option_true(arguments, '--ronin'),
                                  stem=is_option_true(arguments, '--stem'))
    elif is_option_true(arguments, 'bpe'):
        return create_split_value('bpe', bpe_codes_id=get_predefined_bpe_codes_id(arguments))
    else:
        raise AssertionError(f"Invalid split option: {arguments}")
