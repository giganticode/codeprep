import gzip
import logging
import os
import pickle
from typing import List, Tuple

from multiprocessing.pool import Pool

from tqdm import tqdm

from dataprep.dataset import Dataset
from dataprep.preprocessors.core import from_lines, apply_preprocessors
from dataprep.preprocessors.preprocessor_list import pp_params
from dataprep.config import REWRITE_PARSED_FILE, CHUNKSIZE

logger = logging.getLogger(__name__)


def read_file_with_encoding(file_path: str, encoding: str) -> Tuple[List[str], str]:
    with open(file_path, 'r', encoding=encoding) as f:
        return [line for line in f], file_path


def read_file_contents(file_path: str) -> Tuple[List[str], str]:
    try:
        return read_file_with_encoding(file_path, 'utf-8')
    except UnicodeDecodeError:
        logger.warning(f"Encoding is not utf-8, trying ISO-8859-1")
        try:
            return read_file_with_encoding(file_path, 'ISO-8859-1')
        except UnicodeDecodeError:
            logger.error(f"Unicode decode error in file: {file_path}")


def preprocess_and_write(params: Tuple[str, str]) -> None:

    src_file_path, dest_file_path = params

    dest_dirname = os.path.dirname(dest_file_path)
    if not os.path.exists(dest_dirname):
        os.makedirs(dest_dirname, exist_ok=True)

    if not REWRITE_PARSED_FILE and os.path.exists(dest_file_path):
        logger.warning(f"File {dest_file_path} already exists! Doing nothing.")
        return

    with gzip.GzipFile(f'{dest_file_path}.part', 'wb') as f:
        lines_from_file, path = read_file_contents(src_file_path)
        parsed = apply_preprocessors(from_lines(lines_from_file), pp_params["preprocessors"])
        pickle.dump(parsed, f, pickle.HIGHEST_PROTOCOL)

    os.rename(f'{dest_file_path}.part', dest_file_path)


def params_generator(dataset: Dataset):
    for input_file_path in dataset.original.file_iterator_from_file():
        output_file_path = dataset.original.get_new_file_name(input_file_path, dataset.parsed)
        yield (input_file_path, output_file_path)


def run(dataset: Dataset) -> None:
    logger.info(f"Getting files from {dataset.original.path}")
    logger.info(f"Writing preprocessed files to {dataset.parsed.path}")

    files_total = len([f for f in dataset.get_all_files()])
    with Pool() as pool:
        it = pool.imap_unordered(preprocess_and_write, params_generator(dataset), chunksize=CHUNKSIZE)
        for _ in tqdm(it, total=files_total):
            pass
    dataset.parsed.set_ready()