from typing import Optional, Callable, List

from dataprep.bpepkg.bpe_encode import BpeData


Splitter = Callable[[str, BpeData], List[str]]


class ReprConfig(object):
    def __init__(self, types_to_be_repr,
                 bpe_data: Optional[BpeData],
                 should_lowercase: bool,
                 number_splitter: Splitter,
                 word_splitter: Optional[Splitter],
                 full_strings: bool,
                 max_str_length: int):
        self.types_to_be_repr = types_to_be_repr
        self.bpe_data = bpe_data
        self.should_lowercase = should_lowercase
        self.number_splitter = number_splitter
        self.word_splitter = word_splitter
        self.full_strings = full_strings
        self.max_str_length = max_str_length