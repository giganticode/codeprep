import logging
import os
from datetime import datetime

from typing import Optional, List, Generator

from dataprep.config import LIMIT_FILES_ON_LAST_MODIFICATION_CHECK
from dataprep.fileutils import has_one_of_extensions

logger = logging.getLogger(__name__)


def walk(path:bytes, extension: Optional[bytes] = None) -> Generator[bytes, None, None]:
    if os.path.isfile(path) and (not extension or path.endswith(extension)):
        yield path
    else:
        for root, dirs, files in os.walk(path):
            for file in files:
                if not extension or file.endswith(extension):
                    yield os.path.join(root, file)


def walk_and_save(path: str, dir_list_path: str, file_list_path: str, return_dirs_instead_of_regular_files: bool,
                  extensions: Optional[List[str]]) -> Generator[bytes, None, None]:
    with open(dir_list_path, 'w') as d, open(file_list_path, 'w') as f:
        path_bin = path.encode()
        extensions_bin = list(map(lambda e: e.encode(), extensions)) if extensions else None
        # we want to list and store all the files a sequences of bytes to avoid problems with different encodings for filenames
        if os.path.isfile(path_bin):
            res = os.path.basename(path_bin)
            f.write(f'{res}\n')
            if not return_dirs_instead_of_regular_files:
                yield res
        else:
            for root, dirs, files in os.walk(path_bin):
                # we pass bytes to os.walk -> the output are bytes as well
                for dir in dirs:
                    bin_name = os.path.join(os.path.relpath(root, path_bin), dir)
                    d.write(f'{bin_name}\n')
                    if return_dirs_instead_of_regular_files:
                        yield bin_name
                for file in files:
                    bin_name = os.path.join(os.path.relpath(root, path_bin), file)
                    if not extensions or has_one_of_extensions(bin_name, extensions_bin):
                        if not os.path.islink(os.path.join(root, file)):
                            f.write(f'{bin_name}\n')
                            if not return_dirs_instead_of_regular_files:
                                yield bin_name


def get_dir_last_modification(path: str, limit: int = LIMIT_FILES_ON_LAST_MODIFICATION_CHECK) -> datetime:

    def walk_path(path):
        counter = 0
        if os.path.isfile(path) or len(os.listdir(path)) == 0:
            yield os.path.getmtime(path)
        else:
            for root, dirs, files in os.walk(path):
                for dir in dirs:
                    if counter >= limit:
                        return
                    counter += 1
                    yield os.path.getmtime(os.path.join(root, dir))
                for file in files:
                    if counter >= limit:
                        return
                    full_path = os.path.join(root, file)
                    if not os.path.islink(full_path):
                        counter += 1
                        yield os.path.getmtime(full_path)

    mtime = max(walk_path(path))
    return datetime.fromtimestamp(mtime)


def get_timestamp(path: str) -> str:
    last_modif_time = get_dir_last_modification(path)
    return last_modif_time.strftime("%y-%m-%dT%H-%M-%S")


