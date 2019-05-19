import logging
import regex
############   Multitoken list level    ###############3

from dataprep.model.containers import ProcessableTokenContainer, SplitContainer
from dataprep.model.core import ParseableToken
from dataprep.model.word import Word, Underscore

logger = logging.getLogger(__name__)


def simple_split(token_list):
    return [simple_split_token(identifier) for identifier in token_list]

#############  Token Level ################

def simple_split_token(token):
    if isinstance(token, ParseableToken):
        parts = [m[0] for m in
                 regex.finditer('(_|[0-9]+|[[:upper:]]?[[:lower:]]+|[[:upper:]]+(?![[:lower:]]))', str(token))]

        processable_tokens = [Word.from_(p) if p != '_' else Underscore() for p in parts]
        return SplitContainer(processable_tokens)
    elif isinstance(token, ProcessableTokenContainer):
        return type(token)([simple_split_token(subtoken) for subtoken in token.get_subtokens()])
    else:
        return token

