from typing import List

import itertools
import logging
import re

from dataprep.model.containers import ProcessableTokenContainer
from dataprep.model.core import ParseableToken

from dataprep.preprocessors import java
from dataprep.model.chars import MultilineCommentEnd, MultilineCommentStart, \
    OneLineCommentStart, Quote, Backslash, Tab
from dataprep.model.placeholders import placeholders
from dataprep.util import create_regex_from_token_list

logger = logging.getLogger(__name__)

###############   Multitoken list level   ###########


def replace_4whitespaces_with_tabs(token_list):
    result = []
    for token in token_list:
        if isinstance(token, ParseableToken):
            split_line = re.split("( {4})", str(token))
            result.extend([(Tab() if w == " " * 4 else ParseableToken(w)) for w in split_line])
        elif isinstance(token, ProcessableTokenContainer):
            for subtoken in token.get_subtokens():
                result.extend(replace_4whitespaces_with_tabs(subtoken))
        else:
            result.append(token)
    return result


def to_token_str(tokens: List) -> str:
    return repr(" ".join(map(lambda t : str(t),tokens)))[1:-1] + f" {placeholders['ect']}\n"


def to_human_readable(tokens):
    return " ".join(map(lambda t : str(t),tokens)) + "\n"


def spl(token_list, multiline_comments_tokens, two_char_delimiters, one_char_delimiters):
    multiline_comments_regex = create_regex_from_token_list(multiline_comments_tokens)
    two_char_regex = create_regex_from_token_list(two_char_delimiters)
    one_char_regex = create_regex_from_token_list(one_char_delimiters)

    split_nested_list = list(map(
        lambda token: split_to_key_words_and_identifiers(token, multiline_comments_regex,
                                                         two_char_regex, one_char_regex,
                                                         java.delimiters_to_drop_verbose), token_list))
    return [w for lst in split_nested_list for w in lst]

def spl_verbose(token_list):
    '''
    doesn't remove such tokens as tabs, newlines, brackets
    '''
    return spl(token_list,
               java.multiline_comments_tokens,
               java.two_character_tokens + java.two_char_verbose,
               java.one_character_tokens + java.one_char_verbose)

characters = set(java.multiline_comments_tokens + java.two_character_tokens + java.two_char_verbose + java.one_character_tokens + java.one_char_verbose)


def split_to_key_words_and_identifiers(token, multiline_comments_regex,
                                       two_char_regex, one_char_regex, to_drop):
    if isinstance(token, ParseableToken):
        raw_result = []
        result = []
        comment_tokens_separated = re.split(multiline_comments_regex, str(token))
        for st in comment_tokens_separated:
            if re.fullmatch(multiline_comments_regex, st):
                raw_result.append(st)
            else:
                two_char_tokens_separated = re.split(two_char_regex, st)
                for st in two_char_tokens_separated:
                    if re.fullmatch(two_char_regex, st):
                        raw_result.append(st)
                    else:
                        one_char_token_separated = re.split(one_char_regex, st)
                        raw_result.extend(list(filter(None, itertools.chain.from_iterable(
                            [re.split(to_drop, st) for st in one_char_token_separated]
                        ))))
        for raw_str in raw_result:
            if not raw_str in characters:
                result.append(ParseableToken(raw_str))
            elif raw_str == "/*":
                result.append(MultilineCommentStart())
            elif raw_str == "*/":
                result.append(MultilineCommentEnd())
            elif raw_str == "//":
                result.append(OneLineCommentStart())
            elif raw_str == "\"":
                result.append(Quote())
            elif raw_str == "\\":
                result.append(Backslash())
            elif raw_str == "\t":
                result.append(Tab())
            else:
                result.append(raw_str)
        return result
    elif isinstance(token, ProcessableTokenContainer):
        res = []
        for subtoken in token.get_subtokens():
            res.extend(split_to_key_words_and_identifiers(subtoken, multiline_comments_regex, two_char_regex, one_char_regex, to_drop))
        return res
    else:
        return [token]