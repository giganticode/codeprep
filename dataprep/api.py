import collections

from typing import List, Dict, Optional, Union, Tuple

from dataprep.bpepkg.bperegistry import is_predefined_id, CustomBpeConfig
from dataprep.model.core import ParsedToken
from dataprep.model.metadata import PreprocessingMetadata
from dataprep.model.whitespace import NewLine
from dataprep.parse.core import convert_text
from dataprep.prepconfig import PrepConfig, PrepParam
from dataprep.to_repr import init_bpe_data, to_repr


def remove_trailing_newline(prep_tokens: List[Union[ParsedToken, str]]) -> List[Union[ParsedToken, str]]:
    return prep_tokens[:-1] if len(prep_tokens) > 0 and prep_tokens[-1] == NewLine() else prep_tokens


def preprocess(text: str, config: PrepConfig, bpe_codes_id: Optional[str] = None, extension: Optional[str] = None,
               return_metadata: bool=False, force_reinit_bpe_data: bool=True) -> Union[List[str], Tuple[List[str], PreprocessingMetadata]]:
    parsed = [parsed_token for parsed_token in convert_text(text, extension)]
    if config.is_bpe():
        assert bpe_codes_id
        custom_bpe_config = None if is_predefined_id(bpe_codes_id) else CustomBpeConfig.from_id(bpe_codes_id)
        init_bpe_data(config, custom_bpe_config, force_reinit_bpe_data)
    prep_tokens, metadata = to_repr(config, remove_trailing_newline(parsed))
    if return_metadata:
        return prep_tokens, metadata
    else:
        return prep_tokens


def create_split_value(arguments):
    if 'nosplit' in arguments and arguments['nosplit']:
        return '0'
    elif 'chars' in arguments and arguments['chars']:
        return '8'
    elif 'ronin' in arguments and arguments['ronin']:
        return '3'
    elif 'basic' in arguments and arguments['basic']:
        if '--stem' in arguments and arguments['--stem']:
            return 's'
        elif '--split-numbers' in arguments and arguments['--split-numbers']:
            return '2'
        else:
            return '1'
    elif 'bpe' in arguments and arguments['bpe']:
        if arguments['1k']:
            return '5'
        elif arguments['5k']:
            return '4'
        elif arguments['10k']:
            return '6'
        else:
            return '9'
    else:
        raise AssertionError(f"Invalid split option: {arguments}")


def create_com_str_value(arguments):
    if arguments['--no-com'] and arguments['--no-str']:
        return '2'
    elif arguments['--no-com'] and not arguments['--no-str']:
        return '3'
    elif not arguments['--no-com'] and arguments['--no-str']:
        return '1'
    else: # com and str present
        return '0'


def create_prep_config_from_args(arguments: Dict) -> PrepConfig:
    return PrepConfig({
        PrepParam.EN_ONLY: 'U' if '--no-unicode' in arguments and arguments['--no-unicode'] else 'u',
        PrepParam.COM_STR: create_com_str_value(arguments),
        PrepParam.SPLIT: create_split_value(arguments),
        PrepParam.TABS_NEWLINES: '0' if arguments['--no-spaces'] else 's',
        PrepParam.CASE: 'l' if ('--no-case' in arguments and arguments['--no-case']) or ('--stem' in arguments and arguments['--stem']) else 'u'
    })


def nosplit(text: str, extension: Optional[str] = None, no_str: bool=False, no_com: bool=False, no_spaces: bool=False,
            no_unicode: bool=False, return_metadata: bool=False) -> Union[List[str], Tuple[List[str], PreprocessingMetadata]]:
    """
    Split `text` into tokens leaving compound identifiers as they are.

    :param text: text to be split.
    :param extension: extension which a file containing source code written in this programming language would have,
    e.g. 'java', 'py', 'js'.
    If specified, used to select a Pygments parser, otherwise Pygments will try to guess the language.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param: return_metadata: if set to True additionally pre-processing metadata is returned.
    :return: list of tokens `text` was split into. If `return_metadata` is set to True,
    the tuple is returned with the list of preprocessed tokens as the first element
    and pre-processing metadata as the second element (object of :class:`dataprep.model.metadata.Preprocessing.PreprocessingMetadata`)
    """
    d = collections.defaultdict(bool)
    args = {
        '--no-str': no_str,
        '--no-com': no_com,
        '--no-spaces': no_spaces,
        '--no-unicode': no_unicode,
        'nosplit': True
    }
    d.update(args)
    return preprocess(text, create_prep_config_from_args(d), extension=extension, return_metadata=return_metadata)


def ronin(text: str, extension: Optional[str] = None, no_str: bool=False, no_com: bool=False, no_spaces: bool=False,
            no_unicode: bool=False, return_metadata: bool=False) -> Union[List[str], Tuple[List[str], PreprocessingMetadata]]:
    """
    Split `text` into tokens with Ronin algorithm: http://joss.theoj.org/papers/10.21105/joss.00653.
    Numbers are split into digits.

    :param text: text to be split.
    :param extension: extension which a file containing source code written in this programming language would have,
    e.g. 'java', 'py', 'js'.
    If specified, used to select a Pygments parser, otherwise Pygments will try to guess the language.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param: return_metadata: if set to True additionally pre-processing metadata is returned.
    :return: list of tokens `text` was split into. If `return_metadata` is set to True,
    the tuple is returned with the list of preprocessed tokens as the first element
    and pre-processing metadata as the second element (object of :class:`dataprep.model.metadata.Preprocessing.PreprocessingMetadata`)
    """
    d = collections.defaultdict(bool)
    args = {
        '--no-str': no_str,
        '--no-com': no_com,
        '--no-spaces': no_spaces,
        '--no-unicode': no_unicode,
        'ronin': True
    }
    d.update(args)
    return preprocess(text, create_prep_config_from_args(d), extension=extension, return_metadata=return_metadata)


def chars(text: str, extension: Optional[str] = None,
          no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False,
          return_metadata: bool=False) -> Union[List[str], Tuple[List[str], PreprocessingMetadata]]:
    """
    Split `text` into characters (With the exception of operators that consist of 2 character: such operators will remain as a single token).
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, m, y, C, l, a, s, s, </w>]

    :param text: text to be split.
    :param extension: extension which a file containing source code written in this programming language would have,
    e.g. 'java', 'py', 'js'.
    If specified, used to select a Pygments parser, otherwise Pygments will try to guess the language.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param: return_metadata: if set to True additionally pre-processing metadata is returned.
    :return: list of tokens `text` was split into. If `return_metadata` is set to True,
    the tuple is returned with the list of preprocessed tokens as the first element
    and pre-processing metadata as the second element (object of :class:`dataprep.model.metadata.Preprocessing.PreprocessingMetadata`)
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
    return preprocess(text, create_prep_config_from_args(d), '0', extension=extension, return_metadata=return_metadata)


def basic(text: str, extension: Optional[str] = None, split_numbers: bool=False, stem:bool=False,
          no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False,
          return_metadata: bool=False) -> Union[List[str], Tuple[List[str], PreprocessingMetadata]]:
    """
    Split `text` into tokens converting identifiers that follow CamelCase or snake_case into multiple subwords.
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, my, Class, </w>]

    :param text: text to be split.
    :param extension: extension which a file containing source code written in this programming language would have,
    e.g. 'java', 'py', 'js'.
    If specified, used to select a Pygments parser, otherwise Pygments will try to guess the language.

    :param split_numbers: set to True to split numbers into digits
    :param stem: set to True to do stemming with Porter stemmer. Setting this param to True, sets `no_case` and `spit_numbers` to True

    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param: return_metadata: if set to True additionally pre-processing metadata is returned.
    :return: list of tokens `text` was split into. If `return_metadata` is set to True,
    the tuple is returned with the list of preprocessed tokens as the first element
    and pre-processing metadata as the second element (object of :class:`dataprep.model.metadata.Preprocessing.PreprocessingMetadata`)
    """
    d = collections.defaultdict(bool)
    args = {
        '--split-numbers': split_numbers or stem,
        '--stem': stem,
        '--no-str': no_str,
        '--no-com': no_com,
        '--no-spaces': no_spaces,
        '--no-unicode': no_unicode,
        '--no-case': no_case or stem,
        'basic': True
    }
    d.update(args)
    return preprocess(text, create_prep_config_from_args(d), extension=extension, return_metadata=return_metadata)


def bpe(text: str, bpe_codes_id: str, extension: Optional[str] = None,
        no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False,
        return_metadata: bool=False, force_reinit_bpe_data: bool=True) -> Union[List[str], Tuple[List[str], PreprocessingMetadata]]:
    """
    Split `text` into tokens converting identifiers that follow CamelCase or snake_case into multiple subwords.
    On top of that Byte Pair Encoding (BPE) is applied with number of merges specified in `bpe_config`.
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, my, Class, </w>]

    :param text: text to be split.
    :param bpe_codes_id: defines bpe codes to be used when applying bpe,
    predefined codes : 1k, 5k, 10k. Custom bpe codes can be learned by running `dataprep learn-bpe` command.
    :param extension: extension which a file containing source code written in this programming language would have,
    e.g. 'java', 'py', 'js'.
    If specified, used to select a Pygments parser, otherwise Pygments will try to guess the language.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param force_reinit_bpe_data: if set to True, bpe data (merges and bpe cache) is reloaded from the disk
    even if it has been loaded already (for example if this method has been called before). Defaults to True.
    Set this param to False if you want to call this method in a loop.
    Note: if you want to call this method multiple times with different bpe code ids, bpe data has to be reloaded,
    so you must not set this param to False!
    :param return_metadata: if set to True additionally pre-processing metadata is returned.
    :return: list of tokens `text` was split into. If `return_metadata` is set to True,
    the tuple is returned with the list of preprocessed tokens as the first element
    and pre-processing metadata as the second element (object of :class:`dataprep.model.metadata.Preprocessing.PreprocessingMetadata`)
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
    return preprocess(text, create_prep_config_from_args(d), bpe_codes_id, extension=extension,
                      return_metadata=return_metadata, force_reinit_bpe_data=force_reinit_bpe_data)


