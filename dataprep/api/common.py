from typing import Optional

from dataprep.prepconfig import PrepConfig, PrepParam


def create_split_value(split_type: str, bpe_codes_id: Optional[str]=None, stem: bool=False, split_numbers: bool=False):
    if split_type == 'nosplit':
        return '0'
    elif split_type == 'chars':
        return '8'
    elif split_type == 'ronin':
        return '3'
    elif split_type == 'basic':
        if stem:
            return 's'
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


def create_com_str_value(no_com: bool, no_str: bool):
    if no_com and no_str:
        return '2'
    elif no_com and not no_str:
        return '3'
    elif not no_com and no_str:
        return '1'
    else: # com and str present
        return '0'


def create_prep_config(spl_type: str, bpe_codes_id: Optional[str]=None,
                       no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False,
                       stem: bool=False, split_numbers: bool=False):
    return PrepConfig({
        PrepParam.EN_ONLY: 'U' if no_unicode else 'u',
        PrepParam.COM_STR: create_com_str_value(no_com=no_com, no_str=no_str),
        PrepParam.SPLIT: create_split_value(spl_type, bpe_codes_id, stem=stem, split_numbers=split_numbers),
        PrepParam.TABS_NEWLINES: '0' if no_spaces else 's',
        PrepParam.CASE: 'l' if no_case or stem else 'u'
    })