import sys
from typing import List, Optional, Union, Tuple

from dataprep.api.common import create_prep_config
from dataprep.infrastructure.bperegistry import is_predefined_id, CustomBpeConfig
from dataprep.parse.core import convert_text
from dataprep.parse.model.core import ParsedToken
from dataprep.parse.model.metadata import PreprocessingMetadata
from dataprep.parse.model.whitespace import NewLine
from dataprep.prepconfig import PrepConfig
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


def nosplit(text: str, extension: Optional[str] = None, no_spaces: bool = False, no_unicode: bool = False,
            no_com: bool = False, no_str: bool = False, full_strings: bool = False, max_str_length: int = sys.maxsize,
            return_metadata: bool = False) -> Union[List[str], Tuple[List[str], PreprocessingMetadata]]:
    """
    Split `text` into tokens leaving compound identifiers as they are.

    :param text: text to be split.
    :param extension: extension which a file containing source code written in this programming language would have,
    e.g. 'java', 'py', 'js'.
    If specified, used to select a Pygments parser, otherwise Pygments will try to guess the language.

    :param no_spaces: set to True to remove tabs and newlines.
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param full_strings: do not split string literals even on whitespace characters
    :param max_str_length: replace string literal with `""` if its length including quotes exceeds `max_str_length`.
    Does not have effect if `no_str` is set to `True`

    :param return_metadata: if set to True additionally pre-processing metadata is returned.

    :return: list of tokens `text` was split into. If `return_metadata` is set to True,
    the tuple is returned with the list of preprocessed tokens as the first element
    and pre-processing metadata as the second element (object of :class:`dataprep.model.metadata.Preprocessing.PreprocessingMetadata`)
    """
    prep_config= create_prep_config('nosplit', no_spaces=no_spaces, no_unicode=no_unicode, no_com=no_com, no_str=no_str,
                                    full_strings=full_strings, max_str_length=max_str_length)
    return preprocess(text, prep_config, extension=extension, return_metadata=return_metadata)


def chars(text: str, extension: Optional[str] = None, no_spaces: bool = False, no_unicode: bool = False,
          no_case: bool = False, no_com: bool = False, no_str: bool = False, max_str_length=sys.maxsize,
          return_metadata: bool = False) -> Union[List[str], Tuple[List[str], PreprocessingMetadata]]:
    """
    Split `text` into characters (With the exception of operators that consist of 2 character: such operators will remain as a single token).
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, m, y, C, l, a, s, s, </w>]


    :param text: text to be split.
    :param extension: extension which a file containing source code written in this programming language would have,
    e.g. 'java', 'py', 'js'.
    If specified, used to select a Pygments parser, otherwise Pygments will try to guess the language.

    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param max_str_length: replace string literal with `""` if its length including quotes exceeds `max_str_length`.
    Does not have effect if `no_str` is set to `True`

    :param return_metadata: if set to True additionally pre-processing metadata is returned.

    :return: list of tokens `text` was split into. If `return_metadata` is set to True,
    the tuple is returned with the list of preprocessed tokens as the first element
    and pre-processing metadata as the second element (object of :class:`dataprep.model.metadata.Preprocessing.PreprocessingMetadata`)
    """
    prep_config = create_prep_config('chars', no_spaces=no_spaces, no_unicode=no_unicode, no_case=no_case,
                                     no_com=no_com, no_str=no_str, max_str_length=max_str_length)
    return preprocess(text, prep_config, '0', extension=extension, return_metadata=return_metadata)


def basic(text: str, extension: Optional[str] = None, split_numbers: bool = False, ronin: bool = False, stem: bool = False,
          no_spaces: bool = False, no_unicode: bool = False, no_case: bool = False, no_com: bool = False,
          no_str: bool = False, max_str_length: int = sys.maxsize, return_metadata: bool = False) -> Union[List[str], Tuple[List[str], PreprocessingMetadata]]:
    """
    Split `text` into tokens converting identifiers that follow CamelCase or snake_case into multiple subwords.
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, my, Class, </w>]

    :param text: text to be split.
    :param extension: extension which a file containing source code written in this programming language would have,
    e.g. 'java', 'py', 'js'.
    If specified, used to select a Pygments parser, otherwise Pygments will try to guess the language.

    :param split_numbers: set to True to split numbers into digits
    :param ronin: Split words into subwords with Ronin algorithm: http://joss.theoj.org/papers/10.21105/joss.00653.
    :param stem: set to True to do stemming with Porter stemmer. Setting this param to True, sets `no_case` and `spit_numbers` to True

    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param max_str_length: replace string literal with `""` if its length including quotes exceeds `max_str_length`.
    Does not have effect if `no_str` is set to `True`

    :param return_metadata: if set to True additionally pre-processing metadata is returned.

    :return: list of tokens `text` was split into. If `return_metadata` is set to True,
    the tuple is returned with the list of preprocessed tokens as the first element
    and pre-processing metadata as the second element (object of :class:`dataprep.model.metadata.Preprocessing.PreprocessingMetadata`)
    """
    prep_config = create_prep_config('basic', no_spaces=no_spaces, no_unicode=no_unicode, no_case=no_case or stem,
                                     no_com=no_com, no_str=no_str, max_str_length=max_str_length,
                                     split_numbers=split_numbers or ronin or stem, ronin=ronin or stem, stem=stem)
    return preprocess(text, prep_config, extension=extension, return_metadata=return_metadata)


def bpe(text: str, bpe_codes_id: str, extension: Optional[str] = None, no_spaces: bool = False,
        no_unicode: bool = False, no_case: bool = False, no_com: bool = False, no_str: bool = False,
        max_str_length=sys.maxsize, return_metadata: bool = False, force_reinit_bpe_data: bool = True) -> Union[List[str], Tuple[List[str], PreprocessingMetadata]]:
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

    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param max_str_length: replace string literal with `""` if its length including quotes exceeds `max_str_length`.
    Does not have effect if `no_str` is set to `True`

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
    prep_config = create_prep_config('bpe', bpe_codes_id=bpe_codes_id, no_spaces=no_spaces, no_unicode=no_unicode,
                                     no_case=no_case, no_com=no_com, no_str=no_str, max_str_length=max_str_length)
    return preprocess(text, prep_config, bpe_codes_id, extension=extension,
                      return_metadata=return_metadata, force_reinit_bpe_data=force_reinit_bpe_data)


