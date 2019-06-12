import collections

from typing import List, Dict, Optional

from dataprep.bpepkg.bperegistry import create_custom_bpe_config, is_predefined_id
from dataprep.parse.core import convert_text
from dataprep.prepconfig import PrepConfig, PrepParam
from dataprep.to_repr import init_splitting_config, to_repr


def remove_trailing_newline(prep_tokens: List[str]) -> List[str]:
    return prep_tokens[:-1] if len(prep_tokens) > 0 and prep_tokens[-1] == '\n' else prep_tokens


def preprocess(text: str, config: PrepConfig, bpe_codes_id: Optional[str] = None, extension: Optional[str] = None) -> List[str]:
    parsed = convert_text(text, extension)
    custom_bpe_config = None
    if bpe_codes_id and not is_predefined_id(bpe_codes_id):
        custom_bpe_config = create_custom_bpe_config(bpe_codes_id)
    init_splitting_config(config, custom_bpe_config)
    prep_tokens, metadata = to_repr(config, parsed)
    return remove_trailing_newline(prep_tokens)


def create_split_value(arguments):
    if 'nosplit' in arguments and arguments['nosplit']:
        return 0
    elif 'chars' in arguments and arguments['chars']:
        return 8
    elif 'basic' in arguments and arguments['basic']:
        return 1
    elif 'basic+numbers' in arguments and arguments['basic+numbers']:
        return 2
    elif 'bpe' in arguments and arguments['bpe']:
        if arguments['1k']:
            return 5
        elif arguments['5k']:
            return 4
        elif arguments['10k']:
            return 6
        else:
            return 9
    else:
        raise AssertionError(f"Invalid split option: {arguments}")


def create_com_str_value(arguments):
    if arguments['--no-com'] and arguments['--no-str']:
        return 2
    elif arguments['--no-com'] and not arguments['--no-str']:
        return 3
    elif not arguments['--no-com'] and arguments['--no-str']:
        return 1
    else: # com and str present
        return 0


def create_prep_config_from_args(arguments: Dict) -> PrepConfig:
    return PrepConfig({
        PrepParam.EN_ONLY: 3 if '--no-unicode' in arguments and arguments['--no-unicode'] else 0,
        PrepParam.COM_STR: create_com_str_value(arguments),
        PrepParam.SPLIT: create_split_value(arguments),
        PrepParam.TABS_NEWLINES: 1 if arguments['--no-spaces'] else 0,
        PrepParam.CAPS: 1 if '--no-case' in arguments and arguments['--no-case'] else 0
    })


def nosplit(text: str, extension: Optional[str] = None, no_str: bool=False, no_com: bool=False, no_spaces: bool=False) -> List[str]:
    """
    Split `text` into tokens leaving compound identifiers as they are.

    :param text: text to be split.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :return: list of tokens `text` was split into.
    """
    d = collections.defaultdict(bool)
    args = {
        '--no-str': no_str,
        '--no-com': no_com,
        '--no-spaces': no_spaces,
        'nosplit': True
    }
    d.update(args)
    return preprocess(text, create_prep_config_from_args(d), extension=extension)


def chars(text: str, extension: Optional[str] = None, no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False) -> List[str]:
    """
    Split `text` into characters (With the exception of operators that consist of 2 character: such operators will remain as a single token).
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, m, y, C, l, a, s, s, </w>]

    :param text: text to be split.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :return: list of tokens `text` was split into.
    """
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
    return preprocess(text, create_prep_config_from_args(d), extension=extension)


def basic(text: str, extension: Optional[str] = None, no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False) -> List[str]:
    """
    Split `text` into tokens converting identifiers that follow CamelCase or snake_case into multiple subwords.
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, my, Class, </w>]

    :param text: text to be split.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :return: list of tokens `text` was split into.
    """
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
    return preprocess(text, create_prep_config_from_args(d), extension=extension)


def basic_with_numbers(text: str, extension: Optional[str] = None, no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False) -> List[str]:
    """
    Split `text` into tokens converting identifiers that follow CamelCase or snake_case into multiple subwords,
    and numbers into sequence of digits. So that the information about original word boundaries is not lost,
    special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass = 23 -> [<w>, my, Class, </w>, =, <w> 2 3 </w>]

    :param text: text to be split.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :return: list of tokens `text` was split into.
    """
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
    return preprocess(text, create_prep_config_from_args(d), extension=extension)


def bpe(text: str, bpe_codes_id: str, extension: Optional[str] = None, no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False) -> List[str]:
    """
    Split `text` into tokens converting identifiers that follow CamelCase or snake_case into multiple subwords.
    On top of that Byte Pair Encoding (BPE) is applied with number of merges specified in `bpe_config`.
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, my, Class, </w>]

    :param text: text to be split.
    :param bpe_codes_id: defines bpe codes to be used when applying bpe,
    predefined codes : 1k, 5k, 10k. Custom bpe codes can be learned by running `dataprep learn-bpe` command.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :return: list of tokens `text` was split into.
    """
    d = collections.defaultdict(bool)
    args = {
        '--no-str': no_str,
        '--no-com': no_com,
        '--no-spaces': no_spaces,
        '--no-unicode': no_unicode,
        '--no-case': no_case,
        'bpe': True,
        bpe_codes_id: True
    }
    d.update(args)
    return preprocess(text, create_prep_config_from_args(d), bpe_codes_id, extension=extension)


