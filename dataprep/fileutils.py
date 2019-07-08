import logging

from typing import List, Tuple

logger = logging.getLogger(__name__)


def has_one_of_extensions(name: bytes, extensions: List[bytes]) -> bool:
    for ext in extensions:
        if name.endswith(b'.' + ext):
            return True
    return False


def read_file_contents(file_path: bytes) -> Tuple[List[str], bytes]:
    try:
        return read_file_with_encoding(file_path, 'utf-8')
    except UnicodeDecodeError:
        logger.warning(f"Encoding of {file_path} is not utf-8, trying ISO-8859-1")
        try:
            return read_file_with_encoding(file_path, 'ISO-8859-1')
        except UnicodeDecodeError:
            logger.error(f"Unicode decode error in file: {file_path}")


def read_file_with_encoding(file_path: bytes, encoding: str) -> Tuple[List[str], bytes]:
    with open(file_path, 'r', encoding=encoding) as f:
        return [line.rstrip('\n') for line in f], file_path