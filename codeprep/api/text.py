# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import List, Optional, Tuple, Union

import sys

from codeprep.api.common import create_prep_config
from codeprep.parse.core import convert_text
from codeprep.pipeline.bperegistry import is_predefined_id, CustomBpeConfig
from codeprep.pipeline.to_repr import init_bpe_data, to_repr
from codeprep.prepconfig import PrepConfig
from codeprep.preprocess.codestructure import SnippetStructure
from codeprep.preprocess.placeholders import placeholders
from codeprep.preprocess.tokens import TokenSequence
from codeprep.tokentypes.rootclasses import ParsedToken
from codeprep.tokentypes.whitespace import NewLine
from codeprep.tokentypes.word import SpecialToken


def remove_trailing_newline(prep_tokens: List[ParsedToken]) -> List[ParsedToken]:
    return prep_tokens[:-1] if len(prep_tokens) > 0 and prep_tokens[-1] == NewLine() else prep_tokens


def preprocess(text: str, config: PrepConfig, bpe_codes_id: Optional[str] = None, extension: Optional[str] = None,
               force_reinit_bpe_data: bool = True, append_eof: bool = False, path: Optional[Path] = None) \
        -> Union[TokenSequence, Tuple[TokenSequence, SnippetStructure]]:
    parsed = [parsed_token for parsed_token in convert_text(text, extension)]
    parsed = remove_trailing_newline(parsed)
    if append_eof:
        parsed.append(SpecialToken(placeholders['ect']))
    if config.is_bpe():
        assert bpe_codes_id
        custom_bpe_config = None if is_predefined_id(bpe_codes_id) else CustomBpeConfig.from_id(bpe_codes_id)
        init_bpe_data(config, custom_bpe_config, force_reinit_bpe_data)
    preprocessing_results = to_repr(config, parsed)
    if path is None:
        return preprocessing_results.prepped_tokens
    else:
        return  preprocessing_results.prepped_tokens, preprocessing_results.code_snippet_structure.tie_to_working_dir(path, 0, 0)


def nosplit(text: str, extension: Optional[str] = None, no_spaces: bool = False, no_unicode: bool = False,
            no_com: bool = False, no_str: bool = False, full_strings: bool = False, max_str_length: int = sys.maxsize,
            append_eof: bool = False, path: Optional[Path] = None) \
        -> Union[TokenSequence, Tuple[TokenSequence, SnippetStructure]]:
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

    :param append_eof: set to True for <EOF> token to be added to the end of the string
    :param path: associate the input text with a SnippetStructure and set its `path` attribute to the passed value.
    If passed, Tuple[TokenSequence, SnippetStructure] is returned.

    :return: `TokenSequence` representing a split input.

    >>> input_text='''void test_WordUeberraschungPrinter() {
    ...     if (eps >= 0.345e+4) { // FIXME 10L
    ...         printWord("     ...     Überraschung 0x12");
    ...    }
    ... }'''

    >>> prepped_tokens = nosplit(input_text, "java", append_eof=True)
    >>> prepped_tokens.subtokens
    ['void', 'test_WordUeberraschungPrinter', '(', ')', '{', '\\n', \
'\\t', 'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', 'FIXME', '10l', '\\n', '<EOL>', \
'\\t', '\\t', 'printWord', '(', '"', '.', '.', '.', 'Überraschung', '0x12', '"', ')', ';', '\\n', \
'}', '\\n', \
'}', '<EOF>']
    >>> prepped_tokens.metadata.n_subtokens_per_token
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    >>> list(map(lambda x: x.__name__, prepped_tokens.metadata.token_types))
    ['KeyWord', 'Identifier', 'OpeningBracket', 'ClosingBracket', 'OpeningCurlyBracket', 'NewLine', \
'Tab', 'KeyWord', 'OpeningBracket', 'Identifier', 'Operator', 'Operator', 'Number', 'ClosingBracket', 'OpeningCurlyBracket', \
'OneLineComment', 'OneLineComment', 'OneLineComment', 'OneLineComment', 'OneLineComment', 'OneLineComment', \
'Tab', 'Tab', 'Identifier', 'OpeningBracket', 'StringLiteral', 'StringLiteral', 'StringLiteral', 'StringLiteral', \
'StringLiteral', 'StringLiteral', 'StringLiteral', 'ClosingBracket', 'Semicolon', 'NewLine', \
'ClosingCurlyBracket', 'NewLine', \
'ClosingCurlyBracket', 'SpecialToken']


    >>> nosplit('').subtokens
    []

    >>> nosplit(input_text, "java", no_spaces=True).subtokens
    ['void', 'test_WordUeberraschungPrinter', '(', ')', '{', \
'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', 'FIXME', '10l', \
'<EOL>', 'printWord', '(', '"', '.', '.', '.', 'Überraschung', '0x12', '"', ')', ';', \
'}', \
'}']

    >>> nosplit(input_text, "java", no_spaces=True, no_unicode=True).subtokens
    ['void', 'test_WordUeberraschungPrinter', '(', ')', '{', \
'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', 'FIXME', '10l', \
'<EOL>', 'printWord', '(', '"', '.', '.', '.', '<non-en>', '0x12', '"', ')', ';', \
'}', \
'}']

    >>> nosplit('"     ...     Überraschung 0x12"', "java", no_spaces=True, max_str_length=32).subtokens
    ['"', '.', '.', '.', 'Überraschung', '0x12', '"']

    >>> prepped_tokens = nosplit('"     ...     Überraschung 0x12"', "java", no_spaces=True, max_str_length=26)
    >>> prepped_tokens.subtokens
    ['"', '"']
    >>> prepped_tokens.metadata
    ([2], ['StringLiteral'])

    >>> prepped_tokens = nosplit('"     ...     Überraschung 0x12"', "java", no_spaces=True, full_strings=True, max_str_length=31)
    >>> prepped_tokens.subtokens
    ['""']
    >>> prepped_tokens.metadata
    ([1], ['StringLiteral'])

    >>> prepped_tokens = nosplit('"     ...     Überraschung 0x12"', "java", full_strings=True)
    >>> prepped_tokens.subtokens
    ['"\xa0\xa0\xa0\xa0\xa0...\xa0\xa0\xa0\xa0\xa0Überraschung\xa00x12"']
    >>> prepped_tokens.metadata
    ([1], ['StringLiteral'])

    >>> nosplit('"     ...     Überraschung 0x12"', "java", no_spaces=True, full_strings=True, max_str_length=500).subtokens
    ['"\xa0\xa0\xa0\xa0\xa0...\xa0\xa0\xa0\xa0\xa0Überraschung\xa00x12"']


    >>> prepped_tokens = nosplit(input_text, "java", no_spaces=True, no_com=True, no_str=True)
    >>> prepped_tokens.subtokens
    ['void', 'test_WordUeberraschungPrinter', '(', ')', '{', \
'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '<comment>', \
'printWord', '(', '<str-literal>', ')', ';', \
'}', \
'}']
    >>> prepped_tokens.metadata.n_subtokens_per_token
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    >>> list(map(lambda x: x.__name__, prepped_tokens.metadata.token_types))
    ['KeyWord', 'Identifier', 'OpeningBracket', 'ClosingBracket', 'OpeningCurlyBracket', \
'KeyWord', 'OpeningBracket', 'Identifier', 'Operator', 'Operator', 'Number', 'ClosingBracket', 'OpeningCurlyBracket', 'OneLineComment', \
'Identifier', 'OpeningBracket', 'StringLiteral', 'ClosingBracket', 'Semicolon', \
'ClosingCurlyBracket', \
'ClosingCurlyBracket']


    >>> nosplit(input_text, "java", no_spaces=True, no_case=True)
    Traceback (most recent call last):
    ...
    TypeError: nosplit() got an unexpected keyword argument 'no_case'

    >>> nosplit('', path="/path")
    ([], /path: [0], start: (0:0))
    """
    prep_config = create_prep_config('nosplit', no_spaces=no_spaces, no_unicode=no_unicode, no_com=no_com, no_str=no_str,
                                    full_strings=full_strings, max_str_length=max_str_length)
    return preprocess(text, prep_config, extension=extension, append_eof=append_eof, path=path)


def chars(text: str, extension: Optional[str] = None, no_spaces: bool = False, no_unicode: bool = False,
          no_com: bool = False, no_str: bool = False, max_str_length=sys.maxsize, append_eof: bool = False,
          path: Optional[Path] = None) -> Union[TokenSequence, Tuple[TokenSequence, SnippetStructure]]:
    """
    Split `text` into characters (With the exception of operators that consist of 2 character:
    such operators will remain as a single token). So that the information about original word boundaries is not lost,
    special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, m, y, C, l, a, s, s, </w>]


    :param text: text to be split.
    :param extension: extension which a file containing source code written in this programming language would have,
    e.g. 'java', 'py', 'js'.
    If specified, used to select a Pygments parser, otherwise Pygments will try to guess the language.

    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,
    e.g. <non-en>
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param max_str_length: replace string literal with `""` if its length including quotes exceeds `max_str_length`.
    Does not have effect if `no_str` is set to `True`

    :param append_eof: set to True for <EOF> token to be added to the end of the string
    :param path: associate the input text with a SnippetStructure and set its `path` attribute to the passed value.
    If passed, Tuple[TokenSequence, SnippetStructure] is returned.

    :return: `TokenSequence` representing a split input.

    >>> input_text='''void test_WordUeberraschungPrinter() {
    ...     if (eps >= 0.345e+4) { // FIXME 10L
    ...         printWord("     ...     Überraschung 0x12");
    ...    }
    ... }'''

    >>> prepped_tokens = chars(input_text, "java", no_spaces=True, append_eof=True)
    >>> prepped_tokens.subtokens
    ['void</t>', 't', 'e', 's', 't', '_', 'W', 'o', 'r', 'd', 'U', 'e', 'b', 'e', 'r', 'r', 'a', 's', 'c', 'h', \
'u', 'n', 'g', 'P', 'r', 'i', 'n', 't', 'e', 'r', '</t>', '(</t>', ')</t>', '{</t>', \
'if</t>', '(</t>', 'e', 'p', 's', '</t>', '></t>', '=</t>', '0', '.', '3', '4', '5', 'e', '+', '4', '</t>', ')</t>', \
'{</t>', '/</t>', '/</t>', 'F', 'I', 'X', 'M', 'E', '</t>', '1', '0', 'l', '</t>', '<EOL></t>', \
'p', 'r', 'i', 'n', 't', 'W', 'o', 'r', 'd', '</t>', '(</t>', '"', \
'\\xa0', '\\xa0', '\\xa0', '\\xa0', '\\xa0', '.', '.', '.', \
'\\xa0', '\\xa0', '\\xa0', '\\xa0', '\\xa0', 'Ü', 'b', 'e', 'r', 'r', 'a', 's', 'c', 'h', 'u', 'n', 'g', \
'\\xa0', '0', 'x', '1', '2', '"', '</t>', ')</t>', ';</t>', \
'}</t>', \
'}</t>', '<EOF></t>']
    >>> prepped_tokens.metadata.n_subtokens_per_token
    [1, 30, 1, 1, 1, 1, 1, 4, 1, 1, 9, 1, 1, 1, 1, 6, 4, 1, 10, 1, 33, 1, 1, 1, 1, 1]
    >>> list(map(lambda x: x.__name__, prepped_tokens.metadata.token_types))
    ['KeyWord', 'Identifier', 'OpeningBracket', 'ClosingBracket', 'OpeningCurlyBracket', \
'KeyWord', 'OpeningBracket', 'Identifier', 'Operator', 'Operator', 'Number', 'ClosingBracket', 'OpeningCurlyBracket', \
'OneLineComment', 'OneLineComment', 'OneLineComment', 'OneLineComment', 'OneLineComment', \
'Identifier', 'OpeningBracket', 'StringLiteral', 'ClosingBracket', 'Semicolon', \
'ClosingCurlyBracket', 'ClosingCurlyBracket', 'SpecialToken']


    >>> chars('')
    []

    >>> chars('', path="/path")
    ([], /path: [0], start: (0:0))
    """
    prep_config = create_prep_config('chars', no_spaces=no_spaces, no_unicode=no_unicode,
                                     no_com=no_com, no_str=no_str, max_str_length=max_str_length)
    return preprocess(text, prep_config, '0', extension=extension, append_eof=append_eof, path=path)


def basic(text: str, extension: Optional[str] = None,
          split_numbers: bool = False, ronin: bool = False, stem: bool = False,
          no_spaces: bool = False, no_unicode: bool = False, no_case: bool = False, no_com: bool = False,
          no_str: bool = False, max_str_length: int = sys.maxsize, append_eof: bool = False,
          path: Optional[Path] = None) -> Union[TokenSequence, Tuple[TokenSequence, SnippetStructure]]:
    """
    Split `text` into tokens converting identifiers that follow CamelCase or snake_c, path: Optional[Path] = Nonease into multiple subwords.
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original
    words beginnings and ends, e.g. myClass -> [<w>, my, Class, </w>]

    :param text: text to be split.
    :param extension: extension which a file containing source code written in this programming language would have,
    e.g. 'java', 'py', 'js'.
    If specified, used to select a Pygments parser, otherwise Pygments will try to guess the language.

    :param split_numbers: set to True to split numbers into digits
    :param ronin: Split words into subwords with Ronin algorithm: http://joss.theoj.org/papers/10.21105/joss.00653.
    :param stem: set to True to do stemming with Porter stemmer. Setting this param to True, sets `spit_numbers` to True

    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param max_str_length: replace string literal with `""` if its length including quotes exceeds `max_str_length`.
    Does not have effect if `no_str` is set to `True`

    :param append_eof: set to True for <EOF> token to be added to the end of the string
    :param path: associate the input text with a SnippetStructure and set its `path` attribute to the passed value.
    If passed, Tuple[TokenSequence, SnippetStructure] is returned.

    :return: `TokenSequence` representing a split input.


    >>> input_text='''void test_WordUeberraschungPrinter() {
    ...     if (eps >= 0.345e+4) { // FIXME 10L
    ...         printWord("     ...     Überraschung 0x12");
    ...    }
    ... }'''

    >>> prepped_tokens = basic(input_text, "java", no_spaces=True, append_eof=True)
    >>> prepped_tokens.subtokens
    ['void', '<w>', 'test', '_', 'Word', 'Ueberraschung', 'Printer', '</w>', '(', ')', '{', \
'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', 'FIXME', '10l', '<EOL>', \
'<w>', 'print', 'Word', '</w>', '(', '"', '.', '.', '.', 'Überraschung', '0x12', '"', ')', ';', \
'}', \
'}', '<EOF>']

    >>> prepped_tokens.metadata.n_subtokens_per_token
    [1, 7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    >>> list(map(lambda x: x.__name__, prepped_tokens.metadata.token_types))
    ['KeyWord', 'Identifier', 'OpeningBracket', 'ClosingBracket', 'OpeningCurlyBracket', \
'KeyWord', 'OpeningBracket', 'Identifier', 'Operator', 'Operator', 'Number', 'ClosingBracket', 'OpeningCurlyBracket', 'OneLineComment', 'OneLineComment', 'OneLineComment', 'OneLineComment', 'OneLineComment', \
'Identifier', 'OpeningBracket', 'StringLiteral', 'StringLiteral', 'StringLiteral', 'StringLiteral', 'StringLiteral', 'StringLiteral', 'StringLiteral', 'ClosingBracket', 'Semicolon', \
'ClosingCurlyBracket', \
'ClosingCurlyBracket', 'SpecialToken']

    >>> prepped_tokens = basic(input_text, "java", no_spaces=True, no_case=True)
    >>> prepped_tokens.subtokens
    ['void', '<w>', 'test', '_', '<Cap>', 'word', '<Cap>', 'ueberraschung', '<Cap>', 'printer', '</w>', '(', ')', '{', \
'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', '<CAPS>', 'fixme', '10l', '<EOL>', \
'<w>', 'print', '<Cap>', 'word', '</w>', '(', '"', '.', '.', '.', '<Cap>', 'überraschung', '0x12', '"', ')', ';', \
'}', \
'}']

    >>> prepped_tokens.metadata.n_subtokens_per_token
    [1, 10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 5, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1]

    >>> list(map(lambda x: x.__name__, prepped_tokens.metadata.token_types))
    ['KeyWord', 'Identifier', 'OpeningBracket', 'ClosingBracket', 'OpeningCurlyBracket', \
'KeyWord', 'OpeningBracket', 'Identifier', 'Operator', 'Operator', 'Number', 'ClosingBracket', 'OpeningCurlyBracket', 'OneLineComment', 'OneLineComment', 'OneLineComment', 'OneLineComment', 'OneLineComment', \
'Identifier', 'OpeningBracket', 'StringLiteral', 'StringLiteral', 'StringLiteral', 'StringLiteral', 'StringLiteral', 'StringLiteral', 'StringLiteral', 'ClosingBracket', 'Semicolon', \
'ClosingCurlyBracket', \
'ClosingCurlyBracket']

    >>> prepped_tokens = basic(input_text, "java", no_spaces=True, no_case=True, no_com=True, no_str=True)
    >>> prepped_tokens.subtokens
    ['void', '<w>', 'test', '_', '<Cap>', 'word', '<Cap>', 'ueberraschung', '<Cap>', 'printer', '</w>', '(', ')', '{', \
'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '<comment>', \
'<w>', 'print', '<Cap>', 'word', '</w>', '(', '<str-literal>', ')', ';', \
'}', \
'}']

    >>> prepped_tokens = basic('"     Überraschung 0x12"', "java", no_spaces=True, no_unicode=True, no_case=True)
    >>> prepped_tokens.subtokens
    ['"', '<non-en>', '0x12', '"']
    >>> prepped_tokens.metadata
    ([1, 1, 1, 1], ['StringLiteral', 'StringLiteral', 'StringLiteral', 'StringLiteral'])

    >>> basic('')
    []

    >>> prepped_tokens = basic("movingVehiclesspeed = 0.345e+4", "java", split_numbers=True)
    >>> prepped_tokens.subtokens
    ['<w>', 'moving', 'Vehiclesspeed', '</w>', '=', '<w>', '0', '.', '3', '4', '5', 'e', '+', '4', '</w>']
    >>> prepped_tokens.metadata
    ([4, 1, 10], ['Identifier', 'Operator', 'Number'])


    >>> prepped_tokens = basic("movingVehiclesspeed = 0.345e+4", "java", ronin=True)
    >>> prepped_tokens.subtokens
    ['<w>', 'moving', 'Vehicles', 'speed', '</w>', '=', '<w>', '0', '.', '3', '4', '5', 'e', '+', '4', '</w>']

    >>> prepped_tokens = basic("movingVehiclesspeed = 0.345e+4", "java", stem=True)
    >>> prepped_tokens.subtokens
    ['<w>', 'move', 'Vehicl', 'speed', '</w>', '=', '<w>', '0', '.', '3', '4', '5', 'e', '+', '4', '</w>']

    >>> basic('', path="/path")
    ([], /path: [0], start: (0:0))

    """
    prep_config = create_prep_config('basic', no_spaces=no_spaces, no_unicode=no_unicode, no_case=no_case,
                                     no_com=no_com, no_str=no_str, max_str_length=max_str_length,
                                     split_numbers=split_numbers or ronin or stem, ronin=ronin or stem, stem=stem)
    return preprocess(text, prep_config, extension=extension, append_eof=append_eof, path=path)


def bpe(text: str, bpe_codes_id: str, extension: Optional[str] = None, no_spaces: bool = False,
        no_unicode: bool = False, no_com: bool = False, no_str: bool = False,
        max_str_length=sys.maxsize, force_reinit_bpe_data: bool = True, append_eof: bool = False,
        path: Optional[Path] = None) -> Union[TokenSequence, Tuple[TokenSequence, SnippetStructure]]:
    """
    Split `text` into tokens converting identifiers that follow CamelCase or snake_case into multiple subwords.
    On top of that Byte Pair Encoding (BPE) is applied with number of merges specified in `bpe_config`.
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original
    words beginnings and ends,
    e.g. myClass -> [<w>, my, Class, </w>]

    :param text: text to be split.
    :param bpe_codes_id: defines bpe codes to be used when applying bpe,
    predefined codes : 1k, 5k, 10k. Custom bpe codes can be learned by running `codeprep learn-bpe` command.
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
    :param append_eof: set to True for <EOF> token to be added to the end of the string
    :param path: associate the input text with a SnippetStructure and set its `path` attribute to the passed value.
    If passed, Tuple[TokenSequence, SnippetStructure] is returned.

    :return: `TokenSequence` representing a split input.

    >>> input_text='''void test_WordUeberraschungPrinter() {
    ...     if (eps >= 0.345e+4) { // FIXME 10L
    ...         printWord("     ...     Überraschung 0x12");
    ...    }
    ... }'''

    >>> prepped_tokens = bpe(input_text, '10k', "java", no_spaces=True, append_eof=True)
    >>> prepped_tokens.subtokens
    ['void</t>', 'test_', 'Word', 'U', 'eb', 'err', 'as', 'ch', 'un', 'g', 'Print', 'er</t>', \
'(</t>', ')</t>', '{</t>', \
'if</t>', '(</t>', 'e', 'ps</t>', '></t>', '=</t>', '0.', '34', '5', 'e+', '4</t>', ')</t>', \
'{</t>', '/</t>', '/</t>', 'FIX', 'M', 'E</t>', '10', 'l</t>', '<EOL></t>', \
'print', 'Word</t>', '(</t>', '"\\xa0\\xa0\\xa0', '\\xa0\\xa0', '..', '.', '\\xa0\\xa0', '\\xa0\\xa0', \
'\\xa0', 'Ü', 'b', 'err', 'as', 'ch', 'un', 'g', '\\xa0', '0x', '12', '"</t>', ')</t>', ';</t>', \
'}</t>', \
'}</t>', '<EOF></t>']

    >>> prepped_tokens.metadata.n_subtokens_per_token
    [1, 11, 1, 1, 1, 1, 1, 2, 1, 1, 5, 1, 1, 1, 1, 3, 2, 1, 2, 1, 18, 1, 1, 1, 1, 1]

    >>> list(map(lambda x: x.__name__, prepped_tokens.metadata.token_types))
    ['KeyWord', 'Identifier', 'OpeningBracket', 'ClosingBracket', 'OpeningCurlyBracket', \
'KeyWord', 'OpeningBracket', 'Identifier', 'Operator', 'Operator', 'Number', 'ClosingBracket', 'OpeningCurlyBracket', 'OneLineComment', 'OneLineComment', 'OneLineComment', 'OneLineComment', 'OneLineComment', \
'Identifier', 'OpeningBracket', 'StringLiteral', 'ClosingBracket', 'Semicolon', \
'ClosingCurlyBracket', \
'ClosingCurlyBracket', 'SpecialToken']

    >>> prepped_tokens = bpe(input_text, '1k', "java", no_spaces=True, max_str_length=14)
    >>> prepped_tokens.subtokens
    ['void</t>', 'test', '_', 'Wor', 'd', 'U', 'eb', 'err', 'as', 'ch', 'un', 'g', 'P', 'r', 'int', 'er</t>', \
'(</t>', ')</t>', '{</t>', \
'if</t>', '(</t>', 'e', 'p', 's</t>', '></t>', '=</t>', '0.', '3', '4', '5', 'e', '+', '4</t>', ')</t>', \
'{</t>', '/</t>', '/</t>', 'FI', 'X', 'M', 'E</t>', '1', '0', 'l</t>', '<EOL></t>', \
'print', 'Wor', 'd</t>', '(</t>', '"', '"</t>', ')</t>', ';</t>', \
'}</t>', \
'}</t>']
    >>> prepped_tokens.metadata.n_subtokens_per_token
    [1, 15, 1, 1, 1, 1, 1, 3, 1, 1, 7, 1, 1, 1, 1, 4, 3, 1, 3, 1, 2, 1, 1, 1, 1]

    >>> prepped_tokens = bpe(input_text, '5k', "java", no_spaces=True)
    >>> prepped_tokens.subtokens
    ['void</t>', 'test', '_', 'Wor', 'd', 'U', 'eb', 'err', 'as', 'ch', 'un', 'g', 'Print', 'er</t>', \
'(</t>', ')</t>', '{</t>', \
'if</t>', '(</t>', 'e', 'ps</t>', '></t>', '=</t>', '0.', '34', '5', 'e+', '4</t>', ')</t>', \
'{</t>', '/</t>', '/</t>', 'FI', 'X', 'M', 'E</t>', '10', 'l</t>', '<EOL></t>', \
'print', 'Wor', 'd</t>', '(</t>', '"\\xa0', '\\xa0\\xa0', '\\xa0\\xa0', '.', '.', '.', '\\xa0\\xa0', '\\xa0\\xa0', \
'\\xa0', 'Ü', 'b', 'err', 'as', 'ch', 'un', 'g', '\\xa0', '0x', '12', '"</t>', ')</t>', ';</t>', \
'}</t>', \
'}</t>']

    >>> bpe('', '1k')
    []
    >>> bpe('', '1k', path="/path")
    ([], /path: [0], start: (0:0))
    """
    prep_config = create_prep_config('bpe', bpe_codes_id=bpe_codes_id, no_spaces=no_spaces, no_unicode=no_unicode,
                                     no_com=no_com, no_str=no_str, max_str_length=max_str_length)
    return preprocess(text, prep_config, bpe_codes_id, extension=extension,
                      force_reinit_bpe_data=force_reinit_bpe_data, append_eof=append_eof, path=path)