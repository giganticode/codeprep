import gzip
import logging
import os
import pickle

from typing import List, Tuple, Iterator

from multiprocessing.pool import Pool

from tqdm import tqdm

from dataprep.dataset import Dataset, NOT_FINISHED_EXTENSION
from dataprep.parse.core import convert_text
from dataprep.config import REWRITE_PARSED_FILE, CHUNKSIZE, LIMIT_FILES_SCANNING

logger = logging.getLogger(__name__)


#TODO move two methods below to a new fileutils module
def read_file_with_encoding(file_path: bytes, encoding: str) -> Tuple[List[str], bytes]:
    with open(file_path, 'r', encoding=encoding) as f:
        return [line.rstrip('\n') for line in f], file_path


def read_file_contents(file_path: bytes) -> Tuple[List[str], bytes]:
    try:
        return read_file_with_encoding(file_path, 'utf-8')
    except UnicodeDecodeError:
        logger.warning(f"Encoding is not utf-8, trying ISO-8859-1")
        try:
            return read_file_with_encoding(file_path, 'ISO-8859-1')
        except UnicodeDecodeError:
            logger.error(f"Unicode decode error in file: {file_path}")


def preprocess_and_write(params: Tuple[bytes, bytes]) -> None:
    src_file_path, dest_file_path = params

    dest_dirname = os.path.dirname(dest_file_path)
    if not os.path.exists(dest_dirname):
        os.makedirs(dest_dirname, exist_ok=True)

    if not REWRITE_PARSED_FILE and os.path.exists(dest_file_path):
        logger.warning(f"File {dest_file_path} already exists! Doing nothing.")
        return

    not_finished_dest_file_path = dest_file_path + NOT_FINISHED_EXTENSION.encode()
    with gzip.GzipFile(not_finished_dest_file_path, 'wb') as f:
        try:
            lines_from_file, path = read_file_contents(src_file_path)
        except FileNotFoundError:
            logger.error(f"File was found when scanning the directory, but cannot be read: {src_file_path}. "
                         f"Invalid symlink? Ignoring ...")
            return
        extension_bin = os.path.splitext(src_file_path)[1].decode()[1:]
        parsed = [p for p in convert_text("\n".join(lines_from_file), extension_bin)]
        pickle.dump(parsed, f, pickle.HIGHEST_PROTOCOL)

    os.rename(not_finished_dest_file_path, dest_file_path)


def exception_handler(it: Iterator):
    while True:
        try:
            yield next(it)
        except StopIteration:
            return
        except Exception as err:
            logger.error(f"{err}. Ignoring...")


def params_generator(dataset: Dataset):
    for input_file_path in dataset.original.file_iterator():
        output_file_path = dataset.original.get_new_file_name(input_file_path, dataset.parsed)
        yield (input_file_path, output_file_path)


def run(dataset: Dataset) -> None:
    logger.info(f"Getting files from {dataset.original.path}")
    logger.info(f"Writing preprocessed files to {dataset.parsed.path}")

    if dataset.files_need_to_be_saved():
        files_total = 0
        for _ in dataset.get_all_files():
            files_total += 1
            print(f"Files scanned: {files_total}", end='\r')
            if files_total > LIMIT_FILES_SCANNING:
                files_total = None
                print(f"Total files to be preprocessed: {LIMIT_FILES_SCANNING}+")
                break
    else:
        files_total = len([f for f in dataset.get_all_files()])
    with Pool() as pool:
        it = pool.imap_unordered(preprocess_and_write, params_generator(dataset), chunksize=CHUNKSIZE)
        for _ in tqdm(exception_handler(it), total=files_total):
            pass
    dataset.parsed.set_ready()
