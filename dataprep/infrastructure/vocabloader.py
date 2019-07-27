import logging
import os
import shutil
from typing import Set, Dict

from dataprep.infrastructure.bperegistry import get_bpe_dir, get_base_vocab_dir, RESULTING_VOCAB_FILE_NAME
from dataprep.infrastructure.dataset import Dataset, NONBPE_VOCAB_FILENAME
from dataprep.parse.model.placeholders import placeholders
from dataprep.vocab import _load_vocab_dict, _load_vocab_set, VOCAB_FILENAME


logger = logging.getLogger(__name__)

def all(merge_list_id: str) -> Dict[str, int]:
    bpe_dir = get_base_vocab_dir(merge_list_id)
    return _load_vocab_dict(os.path.join(bpe_dir, VOCAB_FILENAME))


def nonbpe(merge_list_id: str) -> Set[str]:
    bpe_dir = get_base_vocab_dir(merge_list_id)
    return _load_vocab_set(os.path.join(bpe_dir, NONBPE_VOCAB_FILENAME))


def base(merge_list_id: str) -> Dict[str, int]:
    all_vocab = all(merge_list_id)
    nonbpe_vocab = nonbpe(merge_list_id)
    for token in nonbpe_vocab:
        if token in all_vocab:
            del all_vocab[token]
    return all_vocab


def bpe(merge_list_id: str, n_merges: int) -> Dict[str, int]:
    bpe_dir = get_bpe_dir(merge_list_id, n_merges)
    return _load_vocab_dict(os.path.join(bpe_dir, RESULTING_VOCAB_FILE_NAME))


def gather_non_bpe_vocab(dataset: Dataset):
    logger.info("Gathering non-bpe vocab...")
    part_nonbpe_vocab_dir = f'{dataset.path_to_nonbpe_vocab_file}_part'
    non_bpe_tokens = set()
    for idx, file in enumerate(os.listdir(part_nonbpe_vocab_dir)):
        if idx % 569 == 0:
            print(f'Files processed: {idx}', end='\r')
        non_bpe_tokens.update(_load_vocab_set(os.path.join(part_nonbpe_vocab_dir, file)))

    non_bpe_tokens.update(list(placeholders.values()))
    with open(dataset.path_to_nonbpe_vocab_file, 'w') as f:
        for token in non_bpe_tokens:
            f.write(f'{token}\n')
    shutil.rmtree(part_nonbpe_vocab_dir)
