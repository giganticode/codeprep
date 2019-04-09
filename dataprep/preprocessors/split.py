import logging
import regex
############   Multitoken list level    ###############3
import time

from dataprep import util
from dataprep.model.containers import ProcessableTokenContainer, SplitContainer
from dataprep.model.word import ParseableToken, Word, Underscore

logger = logging.getLogger(__name__)


class SplittingDict(metaclass=util.Singleton):
    def __init__(self, splitting_file_location):
        self.splitting_dict = {}
        start = time.time()
        with open(splitting_file_location, 'r') as f:
            for ln in f:
                word, splitting = ln.split("|")
                self.splitting_dict[word] = splitting.split()
        logger.info(f"Splitting dictionary is build in {time.time()-start} s")


def get_splitting_dictionary(splitting_file_location):
    return SplittingDict(splitting_file_location).splitting_dict


def simple_split(token_list):
    return [simple_split_token(identifier) for identifier in token_list]

#############  Token Level ################

def simple_split_token(token):
    if isinstance(token, ParseableToken):
        parts = [m[0] for m in
                 regex.finditer('(_|[0-9]+|[[:upper:]]?[[:lower:]]+|[[:upper:]]+(?![[:lower:]]))', str(token))]
        # if len("".join(parts)) ==
        processable_tokens = [Word.from_(p) if p != '_' else Underscore() for p in parts]
        return SplitContainer(processable_tokens)
    elif isinstance(token, ProcessableTokenContainer):
        return type(token)([simple_split_token(subtoken) for subtoken in token.get_subtokens()])
    else:
        return token

