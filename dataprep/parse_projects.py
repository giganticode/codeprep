import argparse
import gzip
import logging
import os
import pickle
from multiprocessing.pool import Pool
from pathlib import Path

from tqdm import tqdm

from dataprep.fs import FS
from dataprep.prepconfig import PrepParam
from dataprep.preprocessors.core import from_lines, apply_preprocessors
from dataprep.preprocessors.preprocessor_list import pp_params
from dataprep.util import file_mapper
from dataprep.config import REWRITE_PARSED_FILE

logger = logging.getLogger(__name__)

EXTENSION = "parsed"
FILENAMES_EXTENSION = "filenames"


def read_file_with_encoding(file_path, encoding):
    with open(file_path, 'r', encoding=encoding) as f:
        return [line for line in f], file_path


def read_file_contents(file_path):
    try:
        return read_file_with_encoding(file_path, 'utf-8')
    except UnicodeDecodeError:
        logger.warning(f"Encoding is not utf-8, trying ISO-8859-1")
        try:
            return read_file_with_encoding(file_path, 'ISO-8859-1')
        except UnicodeDecodeError:
            logger.error(f"Unicode decode error in file: {file_path}")


def preprocess_and_write(params):

    src_dir, dest_dir, train_test_valid, project, preprocessing_param_dict = params
    full_dest_dir = os.path.join(dest_dir, train_test_valid)
    path_to_preprocessed_file = os.path.join(full_dest_dir, f'{project}.{EXTENSION}')
    if not os.path.exists(full_dest_dir):
        os.makedirs(full_dest_dir, exist_ok=True)
    if not REWRITE_PARSED_FILE and os.path.exists(path_to_preprocessed_file):
        logger.warning(f"File {path_to_preprocessed_file} already exists! Doing nothing.")
        return
    dir_with_files_to_preprocess = os.path.join(src_dir, train_test_valid, project)
    if not os.path.exists(dir_with_files_to_preprocess):
        logger.error(f"Path {dir_with_files_to_preprocess} does not exist")
        exit(2)
    filenames=[]
    with gzip.GzipFile(f'{path_to_preprocessed_file}.part', 'wb') as f:
        total_files = sum(f for f in file_mapper(dir_with_files_to_preprocess, lambda path: 1))
        logger.info(f"Preprocessing java files from {dir_with_files_to_preprocess}. Files to process: {total_files}")
        pickle.dump(preprocessing_param_dict, f, pickle.HIGHEST_PROTOCOL)
        for ind, (lines_from_file, file_path) in enumerate(
                file_mapper(dir_with_files_to_preprocess, read_file_contents)):
            if (ind+1) % 100 == 0:
                logger.info(
                    f"[{os.path.join(train_test_valid, project)}] Parsed {ind+1} out of {total_files} files ({(ind+1)/float(total_files)*100:.2f}%)")
            parsed = apply_preprocessors(from_lines(lines_from_file), pp_params["preprocessors"])
            pickle.dump(parsed, f, pickle.HIGHEST_PROTOCOL)
            filename=os.path.relpath(file_path, start=dir_with_files_to_preprocess)
            filenames.append(filename)


    with open(os.path.join(full_dest_dir, f'.{project}.{FILENAMES_EXTENSION}'), "w") as f:
        for filename in filenames:
            try:
                f.write(f"{filename}\n")
            except UnicodeEncodeError:
                f.write("<bad encoding>\n")
                logger.warning("Filename has bad encoding")

    # remove .part to show that all raw files in this project have been preprocessed
    os.rename(f'{path_to_preprocessed_file}.part', path_to_preprocessed_file)


def split_two_last_levels(root):
    root = root + "/"
    return os.path.dirname(os.path.dirname(os.path.dirname(root))), Path(root).parts[-2], Path(root).parts[-1]


def run(path_to_dataset):
    fs = FS.for_parse_projects(path_to_dataset)

    logger.info(f"Getting files from {fs.path_to_dataset}")
    logger.info(f"Writing preprocessed files to {fs.path_to_parsed_dataset}")
    preprocessing_types_dict = {k: None for k in PrepParam}

    params = []

    for train_test_valid, project in fs.get_raw_projects():
        params.append(
            (fs.path_to_dataset, fs.path_to_parsed_dataset, train_test_valid, project, preprocessing_types_dict))

    files_total = len(params)
    with Pool() as pool:
        it = pool.imap_unordered(preprocess_and_write, params)
        for _ in tqdm(it, total=files_total):
            pass


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', help='dataset name')

    args = parser.parse_known_args([])
    args = args[0]

    run(args.path_to_dataset)
