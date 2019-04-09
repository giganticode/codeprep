import collections
from typing import List

from dataprep.prepconfig import PrepConfig, PrepParam
from dataprep.preprocessors.core import from_string, apply_preprocessors
from dataprep.preprocessors.preprocessor_list import pp_params
from dataprep.to_repr import init_splitting_config, to_repr


def preprocess(text: str, config: PrepConfig):
    parsed = apply_preprocessors(from_string(text), pp_params["preprocessors"])
    init_splitting_config(config, None)
    return to_repr(config, parsed)


def create_split_value(arguments):
    if arguments['nosplit']:
        return 0
    elif arguments['chars']:
        return 8
    elif arguments['basic']:
        return 1
    elif arguments['basic+numbers']:
        return 2
    elif arguments['bpe']:
        if arguments['1k']:
            return 5
        elif arguments['5k']:
            return 4
        elif arguments['10k']:
            return 6
        else:
            raise AssertionError(f"Invalid bpe value: {arguments}")
    else:
        raise AssertionError(f"Invlid split option: {arguments}")


def create_com_str_value(arguments):
    if arguments['--no-com'] and arguments['--no-str']:
        return 2
    elif arguments['--no-com'] and not arguments['--no-str']:
        return 3
    elif not arguments['--no-com'] and arguments['--no-str']:
        return 1
    else: # com and str present
        return 0

def create_prep_config_from_args(arguments):
    return PrepConfig({
        PrepParam.EN_ONLY: 3 if arguments['--no-unicode'] else 0,
        PrepParam.COM_STR: create_com_str_value(arguments),
        PrepParam.SPLIT: create_split_value(arguments),
        PrepParam.TABS_NEWLINES: 1 if arguments['--no-spaces'] else 0,
        PrepParam.CAPS: 1 if arguments['--no-case'] else 0
    })


def nosplit(text: str, no_str: bool=False, no_com: bool=False, no_spaces: bool=False) -> List[str]:
    d = collections.defaultdict(bool)
    args = {
        '--no-str': no_str,
        '--no-com': no_com,
        '--no-spaces': no_spaces,
        'nosplit': True
    }
    d.update(args)
    return preprocess(text, create_prep_config_from_args(d))


def chars(text: str, no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False) -> List[str]:
    d = collections.defaultdict(bool)
    args = {
        '--no-str': no_str,
        '--no-com': no_com,
        '--no-spaces': no_spaces,
        '--no-unicode': no_unicode,
        '--no-case': no_case,
        'chars': True
    }
    d.update(args)
    return preprocess(text, create_prep_config_from_args(d))


def basic(text: str, no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False) -> List[str]:
    d = collections.defaultdict(bool)
    args = {
        '--no-str': no_str,
        '--no-com': no_com,
        '--no-spaces': no_spaces,
        '--no-unicode': no_unicode,
        '--no-case': no_case,
        'basic': True
    }
    d.update(args)
    return preprocess(text, create_prep_config_from_args(d))


def basic_with_numbers(text: str, no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False) -> List[str]:
    d = collections.defaultdict(bool)
    args = {
        '--no-str': no_str,
        '--no-com': no_com,
        '--no-spaces': no_spaces,
        '--no-unicode': no_unicode,
        '--no-case': no_case,
        'basic+numbers': True

    }
    d.update(args)
    return preprocess(text, create_prep_config_from_args(d))


def bpe(text: str, bpe_config: str, no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False) -> List[str]:
    d = collections.defaultdict(bool)
    args = {
        '--no-str': no_str,
        '--no-com': no_com,
        '--no-spaces': no_spaces,
        '--no-unicode': no_unicode,
        '--no-case': no_case,
        'bpe': True,
        bpe_config: True
    }
    d.update(args)
    return preprocess(text, create_prep_config_from_args(d))


