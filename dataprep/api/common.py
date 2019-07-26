import sys
from typing import Optional

from dataprep.prepconfig import PrepConfig, PrepParam, get_possible_str_values


def create_split_value(split_type: str, bpe_codes_id: Optional[str] = None, full_strings: bool = False,
                       split_numbers: bool = False, ronin: bool = False, stem: bool = False):
    if split_type == 'nosplit':
        return 'F' if full_strings else '0'
    elif split_type == 'chars':
        return '8'
    elif split_type == 'basic':
        if stem:
            return 's'
        elif ronin:
            return '3'
        elif split_numbers:
            return '2'
        else:
            return '1'
    elif split_type == 'bpe':
        if bpe_codes_id == '1k':
            return '5'
        elif bpe_codes_id == '5k':
            return '4'
        elif bpe_codes_id == '10k':
            return '6'
        else:
            return '9'
    else:
        raise AssertionError(f"Invalid split option: {split_type}")


def create_str_value(no_str: bool, max_str_len: int) -> str:
    if no_str:
        return '0'
    if 0 <= max_str_len < 2:
        return '2'
    if 2 <= max_str_len < len(get_possible_str_values()):
        return get_possible_str_values()[max_str_len]
    else:
        return '1'


def create_prep_config(spl_type: str, bpe_codes_id: Optional[str] = None, no_spaces: bool = False,
                       no_unicode: bool = False, no_case: bool = False, no_com: bool = False, no_str: bool = False,
                       full_strings: bool = False, max_str_length: int = sys.maxsize, split_numbers: bool = False,
                       ronin: bool = False, stem: bool = False):
    return PrepConfig({
        PrepParam.EN_ONLY: 'U' if no_unicode else 'u',
        PrepParam.COM: '0' if no_com else 'c',
        PrepParam.STR: create_str_value(no_str, max_str_length),
        PrepParam.SPLIT: create_split_value(spl_type, bpe_codes_id=bpe_codes_id, full_strings=full_strings,
                                            split_numbers=split_numbers, ronin=ronin, stem=stem),
        PrepParam.TABS_NEWLINES: '0' if no_spaces else 's',
        PrepParam.CASE: 'l' if no_case or stem else 'u'
    })