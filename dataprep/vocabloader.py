import os
import shutil

from typing import Set, Dict

from dataprep.bperegistry import get_bpe_dir_by_id, NONBPE_VOCAB_FILENAME, VOCAB_FILENAME
from dataprep.dataset import Dataset
from dataprep.model.placeholders import placeholders
from dataprep.util import read_dict_from_2_columns


def all(bpe_id: str) -> Dict[str, int]:
    bpe_dir = get_bpe_dir_by_id(bpe_id)
    return read_dict_from_2_columns(os.path.join(bpe_dir, VOCAB_FILENAME))


def nonbpe(bpe_id: str) -> Set[str]:
    bpe_dir = get_bpe_dir_by_id(bpe_id)
    return _load_nonbpe_vocab_from_file(os.path.join(bpe_dir, NONBPE_VOCAB_FILENAME))


def base(bpe_id: str) -> Dict[str, int]:
    all_vocab = all(bpe_id)
    nonbpe_vocab = nonbpe(bpe_id)
    for token in nonbpe_vocab:
        del all_vocab[token]
    return all_vocab


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
