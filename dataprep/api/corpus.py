import logging
import os
import sys
from multiprocessing.pool import Pool
from typing import Optional, Dict, Tuple

from tqdm import tqdm

from dataprep.api.common import create_prep_config
from dataprep.config import CHUNKSIZE
from dataprep.infrastructure import stages
from dataprep.infrastructure.bperegistry import CustomBpeConfig, is_predefined_id
from dataprep.infrastructure.dataset import Dataset, SubDataset
from dataprep.prepconfig import PrepConfig
from dataprep.vocab import _load_vocab_dict

logger = logging.getLogger(__name__)


def _calc_n_tokens(params: Tuple[str,]) -> int:
    file, = params
    total_words = 0
    with open(file, 'r') as f:
        for line in f:
            total_words += len(line.split(" "))
    return total_words


class PreprocessedCorpus(object):
    def __init__(self, prep_dataset: SubDataset, path_to_vocab: str):
        self.path_to_prep_dataset = prep_dataset.path
        self.get_file_iterator = lambda: prep_dataset.file_iterator()
        self.path_to_vocab = path_to_vocab
        self._path_to_corpus_size_file = prep_dataset._dataset.path_to_prep_corpus_size_file

    def load_vocab(self) -> Dict[str, int]:
        if not self.path_to_vocab:
            raise ValueError("Vocabulary has not been yet calculated. Set calc_vocab param to True when running preprocessing.")

        return _load_vocab_dict(self.path_to_vocab)

    def get_corpus_size(self) -> int:
        if not os.path.exists(self._path_to_corpus_size_file):
            corpus_size = self._calc_corpus_size()
            with open(self._path_to_corpus_size_file, 'w') as f:
                f.write(f'{corpus_size}')
        with open(self._path_to_corpus_size_file, 'r') as f:
            return int(f.read())

    def _calc_corpus_size(self):
        files_total = len([f for f in self.get_file_iterator()])
        total_words = 0

        def param_gen():
            for f in self.get_file_iterator():
                yield (f,)

        with Pool() as pool:
            it = pool.imap_unordered(_calc_n_tokens, param_gen(), chunksize=CHUNKSIZE)
            for res in tqdm(it, total=files_total):
                total_words += res

        return total_words


def nosplit(path: str, extensions: Optional[str] = None, no_spaces: bool = False, no_unicode: bool = False,
            no_com: bool = False, no_str: bool = False, full_strings: bool = False, max_str_length: int = sys.maxsize,
            output_path: Optional[str] = None, calc_vocab=False) -> PreprocessedCorpus:
    """
    Split corpus at `path` into tokens leaving compound identifiers as they are.

    :param path: path to the corpus to be split.
    :param extensions: Limits the set of input files to the files with the specified extension(s).
    The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.

    :param no_spaces: set to True to remove tabs and newlines.
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param full_strings: do not split string literals even on whitespace characters. Does not have effect if `no_str` is set to `True`
    :param max_str_length: replace string literal with `""` if its length including quotes exceeds `max_str_length`.
    Does not have effect if `no_str` is set to `True`

    :return: `PreprocessedDataset` object which holds metadata of the preprocessed dataset
    """
    prep_config= create_prep_config('nosplit', no_spaces=no_spaces, no_unicode=no_unicode, no_com=no_com, no_str=no_str,
                                    full_strings=full_strings, max_str_length=max_str_length)
    return preprocess_corpus(path, prep_config, extensions=extensions,
                             output_path=output_path, calc_vocab=calc_vocab)


def chars(path: str, extensions: Optional[str] = None, no_spaces: bool = False, no_unicode: bool = False,
          no_case: bool = False, no_com: bool = False, no_str: bool = False, max_str_length=sys.maxsize,
          output_path: Optional[str] = None, calc_vocab=False) -> PreprocessedCorpus:
    """
    Split corpus at `path` into characters (With the exception of operators that consist of 2 character: such operators will remain as a single token).
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, m, y, C, l, a, s, s, </w>]

    :param path: path to the corpus to be split.
    :param extensions: Limits the set of input files to the files with the specified extension(s).
    The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.

    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param max_str_length: replace string literal with `""` if its length including quotes exceeds `max_str_length`.
    Does not have effect if `no_str` is set to `True`

    :return: `PreprocessedDataset` object which holds metadata of the preprocessed dataset
    """
    prep_config= create_prep_config('chars', no_spaces=no_spaces, no_unicode=no_unicode, no_case=no_case, no_com=no_com,
                                    no_str=no_str, max_str_length=max_str_length)
    return preprocess_corpus(path, prep_config, '0', extensions=extensions, output_path=output_path, calc_vocab=calc_vocab)


def basic(path: str, extensions: Optional[str] = None, split_numbers: bool = False, ronin = False, stem: bool = False,
          no_spaces: bool = False, no_unicode: bool = False, no_case: bool = False, no_com: bool = False,
          no_str: bool = False, max_str_length=sys.maxsize, output_path: Optional[str] = None, calc_vocab=False) -> PreprocessedCorpus:
    """
    Split corpus at `path` into tokens converting identifiers that follow CamelCase or snake_case into multiple subwords.
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, my, Class, </w>]

    :param path: path to the corpus to be split.
    :param extensions: Limits the set of input files to the files with the specified extension(s).
    The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.

    :param split_numbers: set to True to split numbers into digits
    :param ronin: Split words into subwords with Ronin algorithm: http://joss.theoj.org/papers/10.21105/joss.00653.
    Setting `ronin` to `True` implies `split_numbers`=`True`
    :param stem: set to True to do stemming with Porter stemmer.
    Setting `stem` to `True` implies `no_case`=`True`, `ronin`= `True`, and `split_numbers`=`True`

    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param max_str_length: replace string literal with `""` if its length including quotes exceeds `max_str_length`.
    Does not have effect if `no_str` is set to `True`

    :return: `PreprocessedDataset` object which holds metadata of the preprocessed dataset
    """
    prep_config = create_prep_config('basic', no_spaces=no_spaces, no_unicode=no_unicode, no_case=no_case or stem,
                                     no_com=no_com, no_str=no_str, max_str_length=max_str_length,
                                     split_numbers=split_numbers or stem or ronin, ronin=ronin or stem, stem=stem)
    return preprocess_corpus(path, prep_config, extensions=extensions, output_path=output_path, calc_vocab=calc_vocab)


def bpe(path: str, bpe_codes_id: str, extensions: Optional[str] = None, no_spaces: bool = False,
        no_unicode: bool = False, no_case: bool = False, no_com: bool = False, no_str: bool = False,
        max_str_length=sys.maxsize, output_path: Optional[str] = None, calc_vocab=False) -> PreprocessedCorpus:
    """
    Split corpus at `path` into tokens converting identifiers that follow CamelCase or snake_case into multiple subwords.
    On top of that Byte Pair Encoding (BPE) is applied with number of merges specified in `bpe_config`.
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, my, Class, </w>]

    :param path: path to the corpus to be split.
    :param bpe_codes_id: defines bpe codes to be used when applying bpe,
    predefined codes : 1k, 5k, 10k. Custom bpe codes can be learned by running `dataprep learn-bpe` command.
    :param extensions: Limits the set of input files to the files with the specified extension(s).
    The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.


    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param max_str_length: replace string literal with `""` if its length including quotes exceeds `max_str_length`.
    Does not have effect if `no_str` is set to `True`

    :return: `PreprocessedDataset` object which holds metadata of the preprocessed dataset
    """
    prep_config= create_prep_config('bpe', bpe_codes_id=bpe_codes_id, no_spaces=no_spaces, no_unicode=no_unicode,
                                    no_case=no_case, no_com=no_com, no_str=no_str, max_str_length=max_str_length)
    return preprocess_corpus(path, prep_config, bpe_codes_id,
                             extensions=extensions, output_path=output_path, calc_vocab=calc_vocab)


def preprocess_corpus(path: str, prep_config: PrepConfig, bpe_codes_id: Optional[str]=None,
                      extensions: Optional[str]=None, output_path: Optional[str]=None, calc_vocab: Optional[bool]=False) -> PreprocessedCorpus:
    output_path = output_path or os.getcwd()
    custom_bpe_config = None
    if prep_config.is_bpe():
        assert bpe_codes_id
        if not is_predefined_id(bpe_codes_id):
            custom_bpe_config = CustomBpeConfig.from_id(bpe_codes_id)

    dataset = Dataset.create(str(path), prep_config, extensions, custom_bpe_config,
                             overriden_path_to_prep_dataset=output_path)
    if calc_vocab:
        stages.run_until_vocab(dataset, custom_bpe_config)
        path_to_vocab = dataset.path_to_vocab_file
    else:
        stages.run_until_preprocessing(dataset, custom_bpe_config)
        path_to_vocab = None
    logger.info(f"Preprocessed dataset is ready at {dataset.preprocessed.path}")
    return PreprocessedCorpus(dataset.preprocessed, path_to_vocab)
