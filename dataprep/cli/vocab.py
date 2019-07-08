import logging

import argparse

from dataprep.dirutils import walk
from dataprep.vocab import calc_vocab

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_dataset', action='store', help=f'path to dataset')
    parser.add_argument('output_dir', action='store', help=f'output dir')
    parser.add_argument('extension', action='store', help=f'extension')

    args = parser.parse_known_args()
    args = args[0]

    calc_vocab(args.path_to_dataset, walk(args.path_to_dataset.encode(), extension=args.extension.encode()), args.output_dir)
