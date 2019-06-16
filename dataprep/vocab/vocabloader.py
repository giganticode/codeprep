import os

import shutil
from typing import Set, Dict

from dataprep.bpepkg.bpe_learn import BPE_REASSEMBLED_VOCAB_FILE_NAME
from dataprep.bpepkg.bperegistry import get_dataset_bpe_dir, get_bpe_dir
from dataprep.dataset import Dataset, NONBPE_VOCAB_FILENAME, VOCAB_FILENAME
from dataprep.model.placeholders import placeholders
from dataprep.util import read_dict_from_2_columns


def all(merge_list_id: str) -> Dict[str, int]:
    bpe_dir = get_dataset_bpe_dir(merge_list_id)
    return read_dict_from_2_columns(os.path.join(bpe_dir, VOCAB_FILENAME))


def nonbpe(merge_list_id: str) -> Set[str]:
    bpe_dir = get_dataset_bpe_dir(merge_list_id)
    return _load_nonbpe_vocab_from_file(os.path.join(bpe_dir, NONBPE_VOCAB_FILENAME))


def base(merge_list_id: str) -> Dict[str, int]:
    all_vocab = all(merge_list_id)
    nonbpe_vocab = nonbpe(merge_list_id)
    for token in nonbpe_vocab:
        if token in all_vocab:
            del all_vocab[token]
    return all_vocab


def bpe(merge_list_id: str, n_merges: int) -> Dict[str, int]:
    bpe_dir = get_bpe_dir(merge_list_id, n_merges)
    return read_dict_from_2_columns(os.path.join(bpe_dir, BPE_REASSEMBLED_VOCAB_FILE_NAME))


def gather_non_bpe_vocab(dataset: Dataset):
    print("Gathering non-bpe vocab...", end='')
    part_nonbpe_vocab_dir = f'{dataset.path_to_nonbpe_vocab_file}_part'
    non_bpe_tokens = set()
    for idx, file in enumerate(os.listdir(part_nonbpe_vocab_dir)):
        if idx % 5000 == 0:
            print('.', end='')
        non_bpe_tokens.update(_load_nonbpe_vocab_from_file(os.path.join(part_nonbpe_vocab_dir, file)))
    print()
    non_bpe_tokens.update(list(placeholders.values()))
    with open(dataset.path_to_nonbpe_vocab_file, 'w') as f:
        for token in non_bpe_tokens:
            f.write(f'{token}\n')
    shutil.rmtree(part_nonbpe_vocab_dir)


def _load_nonbpe_vocab_from_file(file: str):
    non_bpe_tokens = set()
    with open(file, 'r') as f:
        for line in f:
            non_bpe_tokens.add(line.rstrip('\n'))
    return non_bpe_tokens
