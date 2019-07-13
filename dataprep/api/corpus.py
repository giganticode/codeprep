import os
from typing import Optional, List, Dict, Callable, Generator

from dataprep.api.common import create_prep_config
from dataprep.installation import stages
from dataprep.installation.bperegistry import CustomBpeConfig, is_predefined_id
from dataprep.installation.dataset import Dataset
from dataprep.prepconfig import PrepConfig
from dataprep.vocab import _load_vocab_dict


class PreprocessedCorpus(object):
    def __init__(self, path_to_prep_dataset: str,
                 get_file_iterator: Callable[[], Generator[bytes, None, None]],
                 path_to_vocab:str):
        self.path_to_prep_dataset = path_to_prep_dataset
        self.get_file_iterator = get_file_iterator
        self.path_to_vocab = path_to_vocab

    def load_vocab(self) -> Dict[str, int]:
        if not self.path_to_vocab:
            raise ValueError("Vocabulary has not been yet calculated. Set calc_vocab param to True when running preprocessing.")

        return _load_vocab_dict(self.path_to_vocab)


def nosplit(path: str, extensions: Optional[str] = None, no_str: bool=False, no_com: bool=False, no_spaces: bool=False,
            no_unicode: bool=False, output_path: Optional[str]=None, calc_vocab=False) -> PreprocessedCorpus:
    """
    Split corpus at `path` into tokens leaving compound identifiers as they are.

    :param path: path to the corpus to be split.
    :param extensions: Limits the set of input files to the files with the specified extension(s).
    The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.

    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>

    :return: `PreprocessedDataset` object which holds metadata of the preprocessed dataset
    """
    prep_config=create_prep_config('nosplit', no_str=no_str, no_com=no_com, no_spaces=no_spaces, no_unicode=no_unicode)
    return preprocess_corpus(path, prep_config, extensions=extensions,
                             output_path=output_path, calc_vocab=calc_vocab)


def ronin(path: str, extensions: Optional[str] = None, no_str: bool=False, no_com: bool=False, no_spaces: bool=False,
            no_unicode: bool=False, output_path: Optional[str]=None, calc_vocab=False) -> PreprocessedCorpus:
    """
    Split corpus at `path` into tokens with Ronin algorithm: http://joss.theoj.org/papers/10.21105/joss.00653.
    Numbers are split into digits.

    :param path: path to the corpus to be split.
    :param extensions: Limits the set of input files to the files with the specified extension(s).
    The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.

    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>

    :return: `PreprocessedDataset` object which holds metadata of the preprocessed dataset
    """
    prep_config=create_prep_config('ronin', no_str=no_str, no_com=no_com, no_spaces=no_spaces, no_unicode=no_unicode)
    return preprocess_corpus(path, prep_config, extensions=extensions,
                             output_path=output_path, calc_vocab=calc_vocab)


def chars(path: str, extensions: Optional[str] = None,
          no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False,
          output_path: Optional[str]=None, calc_vocab=False) -> PreprocessedCorpus:
    """
    Split corpus at `path` into characters (With the exception of operators that consist of 2 character: such operators will remain as a single token).
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, m, y, C, l, a, s, s, </w>]

    :param path: path to the corpus to be split.
    :param extensions: Limits the set of input files to the files with the specified extension(s).
    The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.

    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>

    :return: `PreprocessedDataset` object which holds metadata of the preprocessed dataset
    """
    prep_config=create_prep_config('chars',
                                   no_str=no_str, no_com=no_com, no_spaces=no_spaces,
                                   no_unicode=no_unicode, no_case=no_case)
    return preprocess_corpus(path, prep_config, '0', extensions=extensions, output_path=output_path, calc_vocab=calc_vocab)


def basic(path: str, extensions: Optional[str] = None, split_numbers: bool=False, stem:bool=False,
          no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False,
          output_path: Optional[str]=None, calc_vocab=False) -> PreprocessedCorpus:
    """
    Split corpus at `path` into tokens converting identifiers that follow CamelCase or snake_case into multiple subwords.
    So that the information about original word boundaries is not lost, special tokens are inserted to denote original words beginnings and ends,
    e.g. myClass -> [<w>, my, Class, </w>]

    :param path: path to the corpus to be split.
    :param extensions: Limits the set of input files to the files with the specified extension(s).
    The format is the following: "ext1|ext2|...|extN" If not specififed, all the files are read.

    :param split_numbers: set to True to split numbers into digits
    :param stem: set to True to do stemming with Porter stemmer. Setting this param to True, sets `no_case` and `spit_numbers` to True

    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>

    :return: `PreprocessedDataset` object which holds metadata of the preprocessed dataset
    """
    prep_config = create_prep_config('basic',
                                     no_str=no_str, no_com=no_com, no_spaces=no_spaces,
                                     no_unicode=no_unicode, no_case=no_case or stem,
                                     split_numbers=split_numbers or stem, stem=stem)
    return preprocess_corpus(path, prep_config, extensions=extensions, output_path=output_path, calc_vocab=calc_vocab)


def bpe(path: str, bpe_codes_id: str, extensions: Optional[str] = None,
        no_str: bool=False, no_com: bool=False, no_spaces: bool=False, no_unicode: bool=False, no_case: bool=False,
        output_path: Optional[str]=None, calc_vocab=False) -> PreprocessedCorpus:
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

    :param no_str: set to True to replace each string literals with a special token, e.g <str_literal>.
    :param no_com: set to True to replace each comment with a special token, e.g. <comment>.
    :param no_spaces: set to True to remove tabs and newlines.
    :param no_case: set to True to lowercase identifiers and encode information about their case in a separate token,
    e.g. Identifier -> [<Cap>, identifier]; IDENTIFIER -> [<CAPS>, identifier]
    :param no_unicode: set to True to replace each word containing non-ascii characters to a special token,  e.g. <non-en>

    :return: `PreprocessedDataset` object which holds metadata of the preprocessed dataset
    """
    prep_config=create_prep_config('bpe', bpe_codes_id=bpe_codes_id,
                                   no_str=no_str, no_com=no_com, no_spaces=no_spaces,
                                   no_unicode=no_unicode, no_case=no_case)
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
    print(f"Preprocessed dataset is ready at {dataset.preprocessed.path}")
    return PreprocessedCorpus(dataset.preprocessed.path, lambda : dataset.preprocessed.file_iterator(), path_to_vocab)
