<!--
SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>

SPDX-License-Identifier: Apache-2.0
-->

# Codeprep

[![Build Status](https://travis-ci.org/giganticode/codeprep.svg?branch=master)](https://travis-ci.org/giganticode/codeprep)
[![Maintainability](https://api.codeclimate.com/v1/badges/64c9b107bc09fdb1b3b1/maintainability)](https://codeclimate.com/github/giganticode/codeprep/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/64c9b107bc09fdb1b3b1/test_coverage)](https://codeclimate.com/github/giganticode/codeprep/test_coverage)
[![PyPI version fury.io](https://badge.fury.io/py/codeprep.svg)](https://pypi.python.org/pypi/codeprep/)

**This is a tool for preprocessing source code corpora according to a specified vocabulary modeling choice.**

Supported modeling choices are: 
* Splitting algorithm (no identifier splitting, camel-case splitting, snake-case splitting, BPE (byte-pair-encoding), 
number-splitting, ronin: http://joss.theoj.org/papers/10.21105/joss.00653); 
* Number of merges if using BPE; 
* Ignoring/preserving string literals; 
* Ignoring/preserving comments; 
* Preserving case/lowercasing;
* Preserving/ignoring newlines and tabs.
* applying/not applying stemming after basic splitting 

# Getting started

Make sure you have python >= 3.6 installed in your system; pip, setuptools and wheel are up to date.
```bash
python --version
python -m pip install --upgrade pip setuptools wheel
```

Install **codeprep** lib:
```bash
pip install codeprep
```

In order to run the **ronin** algorithm, you will have to additionally install Spiral module (https://github.com/casics/spiral/):
```bash
pip install git+https://github.com/casics/spiral.git
```

The tool can be used **as a python library** as well as a standalone module runnable with a **CLI**. 
You can pass the path to the dataset or the text itself to be preprocessed. When using Python API for the former option 
you need to import methods from `codeprep.api.text` module, for the latter - from `codeprep.api.corpus`.
Below you can see the general patterns of usage.


Python API
```python
>>> import codeprep.api.text as cp
>>> cp.<commmand>('Some code to be split')
```

```python
>>> import codeprep.api.corpus as cp
>>> cp.<commmand>('/path/to/the/dataset')
```

CLI
```bash
codeprep <commmand> "Some code to be split"
```

```bash
codeprep <commmand> --path /path/to/the/dataset
```


Hereafter we will demonstrate the usage as a python library. The CLI is analogous to the python API. You can find the documentation about how to use it [here](codeprep/cli/spec.py). 

## Usage examples

### Basic splitting 
Tokenization + CamelCase- and snake_case- splitting:

```python
>>> import codeprep.api.text as cp
>>> input_code = '''void test_WordUeberraschungPrinter() {
...     if (eps >= 0.345e+4) { // FIXME
...         printWord("     ...     Überraschung");
...     }
... }'''
>>> cp.basic(input_code)
['void', '<w>', 'test', '_', 'Word', 'Ueberraschung', 'Printer', '</w>', '(', ')', '{', '\n', 
'\t', 'if', '(', 'eps', '>', '=', '0', '.', '<w>', '345', 'e', '</w>', '+', '4', ')', '{', '/', '/', 'FIXME', '\n', 
'\t', '\t', '<w>', 'print', 'Word', '</w>', '(', '"', '\t', '.', '.', '.', '\t', 'Überraschung', '"', ')', ';', '\n', 
'\t', '}', '\n', 
'}']
```

### Tokenize but don't split identifiers

```python
>>> import codeprep.api.text as cp
>>> input_code = '''void test_WordUeberraschungPrinter() {
...     if (eps >= 0.345e+4) { // FIXME
...         printWord("     ...     Überraschung");
...     }
... }'''
>>> cp.nosplit(input_code)
['void', 'test_WordUeberraschungPrinter', '(', ')', '{', '\n', 
'\t', 'if', '(', 'eps', '>', '=', '0', '.', '345e', '+', '4', ')', '{', '/', '/', 'FIXME', '\n', 
'\t', '\t', 'printWord', '(', '"', '\t', '.', '.', '.', '\t', 'Überraschung', '"', ')', ';', '\n', 
'\t', '}', '\n', 
'}']
```

### BPE (Byte-Pair encoding)

The following code does **camelCase-** and **snake_case-** splitting and applies **bpe with 10k merges** on top:

```python
>>> import codeprep.api.text as cp
>>> input_code = '''void test_WordUeberraschungPrinter() {
...     if (eps >= 0.345e+4) { // FIXME
...         printWord("     ...     Überraschung");
...     }
... }'''
>>> cp.bpe(input_code, bpe_codes_id='10k')
['v', 'oid</t>', 'test_', 'Word', 'U', 'eb', 'err', 'as', 'ch', 'un', 'g', 'Print', 'er</t>', '(</t>', ')</t>', '{</t>', '\n', 
'\t', 'i', 'f</t>', '(</t>', 'e', 'ps</t>', '></t>', '=</t>', '0</t>', '.</t>', '34', '5', 'e</t>', '+</t>', '4</t>', ')</t>', '{</t>', '/</t>', '/</t>', 'FIX', 'M', 'E</t>',  '\n', 
'\t', '\t', 'print', 'Word</t>', '(</t>', '"</t>', '\t', '.</t>', '.</t>', '.</t>', '\t', 'Ü', 'b', 'err', 'as', 'ch', 'un', 'g</t>', '"</t>', ')</t>', ';</t>', '\n', 
'\t', '}</t>', '\n', 
'}</t>']
```

**codeprep** by default does BPE using bpe codes leaned on [the Github Java Corpus](http://groups.inf.ed.ac.uk/cup/javaGithub/). The argument `bpe_codes_id='10k'` tells the **codeprep** tool to use 10,000 bpe merges. 
Other possible values are `1k` and `5k` (1,000 and 5,000 merges respectively). Please refer to section [Learning custom BPE codes](#Learning-custom-BPE-codes) to train custom bpe codes.

**For other commands and options like `chars`, `--split-numbers`, `--ronin`, `--stem`, please refer to the [docs](codeprep/cli/spec.py)**.

## Calculate vocabulary 
Set `calc_vocab` param to `True` when calling a preprocessing method to calculate the vocabulary of the preprocessed corpus, e.g.:
```python
>>> import codeprep.api.corpus as cp
>>> cp.basic('/path/to/train/on', calc_vocab=True)
...
Vocab is available at /path/to/vocab
```

## Learning custom BPE codes
If you don't want to use, pre-trained BPE codes, it's possible to train custom ones. For example, to train 10,000 merges on the corpus located at the path `/path/to/train/on`, the following command should be run (only CLI):

```bash
codeprep learn-bpe 10000 -p /path/to/train/on --id custom-bpe-codes 
```

Now it is possible to do bpe splitting by running the bpe command with the number of merges from 0 to 10,000 (for example with 3500 merges):

```bash
codeprep bpe custom-bpe-codes-3500 -p /path/to/preprocess 
```

Before bpe codes are trained, the [basic preprocessing](#basic-splitting) is done, which can also be tuned with arguments described in section [Tweaking preprocessing](#tweaking-preprocessing).


## Additional options
### Tweaking preprocessing
You can pass the following parameters with a `True` value (default values for all of them are False), to tweak the way the imput is preprocessed:

 * `no_str` - replace strings with <string> placeholders.
 * `no_com` - replace comments with <comment> placeholders.
 * `no_spaces` - remove newlines and tabs.
 * `no_unicode` - replace words containing non-ascii characters with <non-en> placeholders.
 * `no_case` - lowercase words and encode information about case in <Cap> <CAP> tokens.
```python
>>> import codeprep.api.text as cp
>>> input_code = '''void test_WordUeberraschungPrinter() {
...     if (eps >= 0.345e+4) { // FIXME
...         printWord("     ...     Überraschung");
...     }
... }'''
>>> cp.basic(input_code, no_spaces=True, no_unicode=True, no_case=True, no_com=True, no_str=True)
['void', '<w>', 'test', '_', '<Cap>', 'word', '<Cap>', 'ueberraschung', '<Cap>', 'printer', '</w>', '(', ')', '{', 
'if', '(', 'eps', '>', '=', '0', '.', '<w>', '345', 'e', '</w>', '+', '4', ')', '{', '/', '/', '<CAPS>', 'fixme', 
'<w>', 'print', '<Cap>', 'word', '</w>', '(', '"', '.', '.', '.', '<Cap>', '<non-en>', '"', ')', ';', 
'}', 
'}']
```

Similar params can be specified as switches `--no-str`, `--no-com`, `--no-spaces`, `--no-unicode`, `--no-case` in CLI commands.

### Specifying the language
Unless explicitely specified, **codeprep** will assume the language is java. To make sure the input is preprocessed as intended, it is always **highly recommended** to specify it:
```python
import codeprep.api.text as cp
>>> cp.bpe("volatile", '1k')
['volatile']
>>> cp.bpe("volatile", '1k', extension="py")
['v', 'ol', 'a', 'ti', 'le</t>']
# Since 'volatile' is a keyword in java, it is represented as one token unlike in python 
# where it is pretty rare when used as an identifier and therefore represented as multiple subtokens.
```

When preprocessing a corpus, `codeprep` identifies the language based on the file extension. If you want only files with (a) certain extension(s) to be preprocessed, you can specify --ext param 
```bash
codeprep basic --path /path/to/be/preprocessed --ext "java"

# or if you want to pre-process multiple types of files: 
codeprep basic --path /path/to/be/preprocessed --ext "java|c|py|js"
```
### Miscellaneous
You can specify the path to where the preprocessed corpus will be written:
```bash
codeprep basic --path /path/to/preprocess --output-path /path/to/output
```

To print logs with log level DEBUG and higher to stdout:
```bash
codeprep basic --path /path/to/preprocess --verbose
```

## Getting Help
To get help on commands and options:

```bash
codeprep --help
```

## Paper

This library was build to run experiments for our paper accepted at ICSE 2020: [Big Code != Big Vocabulary: Open-Vocabulary Models for Source Code](https://arxiv.org/pdf/2003.07914.pdf)

If you you the library or the results, please cite the paper:

 ```
 @article{karampatsis2020big,
  title={Big Code!= Big Vocabulary: Open-Vocabulary Models for Source Code},
  author={Karampatsis, Rafael-Michael and Babii, Hlib and Robbes, Romain and Sutton, Charles and Janes, Andrea},
  journal={arXiv preprint arXiv:2003.07914},
  year={2020}
}
 ```


# Advanced

### Caching

When preprocessing a dataset, **codeprep** first parses source code and converts it into internal representation, 
which is after that converted to a preprocessed dataset depending on provided parameters. The intermediate 
representation is cached, so that when the same dataset is pre-processed again with different parameters,
**codeprep** (providing no changes have been made to the dataset) would use the cache rather than parsing 
the source code again.

To store the cache, **codeprep** uses a directory speecified by `$XDG_CACHE_HOME/codeprep/<codeprep_version>` variable if its value is set, 
`$HOME/.cache/codeprep/<codeprep_version>` otherwise.

Removing the cache will not change the final result, however, will result in slower pre-processing.

# Releases

## 1.0.3
- Add more flixibility with versions of dependencies

## 1.0.1
- Fix training custom bpe codes (Thanks to @mir-am)
- Fix corpus pre-processing on Windows

## 1.0.0
- DOI assigned

## 1.0.0-alpha.12
- Bugfixes and minor improvements

## 1.0.0-alpha.11 (NOT backward compatible with 1.0.0-alpha.10)

- Include token types in the metadata
- Expand on token type hierarchy
- Make possible to return full token index in the iterator

## 1.0.0-alpha.10 (NOT backward compatible with 1.0.0-alpha.9)

- Add boundaries of comments to pre-processing metadata
- Add Windows and OSx support
- Switch from unittest to pytest+doctest
- Bugfixes related to literal presentation of tokens on the disk
- Bugfixes related to adding </t> to mark the end of a full token

## 1.0.0-alpha.9 (NOT backward compatible with 1.0.0-alpha.7)

- Add `get_corpus_size()` method to `PreprocessedCorpus` class
- Do BPE splitting without splitting by convention first
- Use </t> to mark the last sub-token of a token
- Replacing non-ascii sequences with a special char
- Follow symlinks when reading a dataset
- make possible to preserve case when doing stemming
- Bugfixes

## 1.0.0-alpha.7 (NOT backward compatible with 1.0.0-alpha.6)

- Store version in `codeprep.__version__`
- implement `--full-strings` and `--max-str-length` options
- replace `ronin` method/command wit`--ronin` option and apply ronin algorithm on word level instead of full identifier level
- if `split_numbers` option is set to `True`, split numbers not only in code but also in strings and comments
- change placeholder values to more human-readable
- improve logging displaying
- Bugfixes

## 1.0.0-alpha.6

Initial PyPI release
