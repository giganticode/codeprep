# Dataprep

[![Build Status](https://travis-ci.org/giganticode/dataprep.svg?branch=master)](https://travis-ci.org/giganticode/dataprep)

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

Install **dataprep** lib:
```bash
git clone https://github.com/giganticode/dataprep
cd dataprep
pip install .
```

The tool can be used **as a python library** as well as a standalone module runnable with a **CLI**. 
You can pass the path to the dataset or the text itself to be preprocessed. When using Python API for the former option 
you need to import methods from `dataprep.api.text` module, for the latter - from `dataprep.api.corpus`.
Below you can see the general patterns of usage.


Python API
```python
>>> import dataprep.api.text as pp
>>> pp.<commmand>('Some code to be split')
```

```python
>>> import dataprep.api.corpus as pp
>>> pp.<commmand>('/path/to/the/dataset')
```

CLI
```bash
dataprep <commmand> "Some code to be split"
```

```bash
dataprep <commmand> --path /path/to/the/dataset
```

Hereafter we will demonstrate the usage as a python library. The CLI is analogous to the python API. You can find the documentation about how to use it [here](dataprep/cli/spec.py). 

## Usage examples

### Basic splitting 
Tokenization + CamelCase- and snake_case- splitting:

```python
>>> import dataprep.api.text as pp
>>> input_code = '''void test_WordUeberraschungPrinter() {
...     if (eps >= 0.345e+4) { // FIXME
...         printWord("     ...     Überraschung");
...     }
... }'''
>>> pp.basic(input_code)
['void', '<w>', 'test', '_', 'Word', 'Ueberraschung', 'Printer', '</w>', '(', ')', '{', '\n', 
'\t', 'if', '(', 'eps', '>', '=', '0', '.', '<w>', '345', 'e', '</w>', '+', '4', ')', '{', '/', '/', 'FIXME', '\n', 
'\t', '\t', '<w>', 'print', 'Word', '</w>', '(', '"', '\t', '.', '.', '.', '\t', 'Überraschung', '"', ')', ';', '\n', 
'\t', '}', '\n', 
'}']
```

### Tokenize but don't split identifiers

```python
>>> import dataprep.api.text as pp
>>> input_code = '''void test_WordUeberraschungPrinter() {
...     if (eps >= 0.345e+4) { // FIXME
...         printWord("     ...     Überraschung");
...     }
... }'''
>>> pp.nosplit(input_code)
['void', 'test_WordUeberraschungPrinter', '(', ')', '{', '\n', 
'\t', 'if', '(', 'eps', '>', '=', '0', '.', '345e', '+', '4', ')', '{', '/', '/', 'FIXME', '\n', 
'\t', '\t', 'printWord', '(', '"', '\t', '.', '.', '.', '\t', 'Überraschung', '"', ')', ';', '\n', 
'\t', '}', '\n', 
'}']
```

### BPE (Byte-Pair encoding)

The following code does **camelCase-** and **snake_case-** splitting and applies **bpe with 10k merges** on top:

```python
>>> import dataprep.api.text as pp
>>> input_code = '''void test_WordUeberraschungPrinter() {
...     if (eps >= 0.345e+4) { // FIXME
...         printWord("     ...     Überraschung");
...     }
... }'''
>>> pp.bpe(input_code, bpe_codes_id='10k')
['void', '<w>', 'test', '_', 'Word', 'U', 'e', 'ber', 'r', 'as', 'ch', 'ung', 'Printer', '</w>', '(', ')', '{', '\n', 
'\t', 'if', '(', '<w>', 'ep', 's', '</w>', '>', '=', '0', '.', '<w>', '34', '5', 'e', '</w>', '+', '4', ')', '{', '/', '/', 'FIXME', '\n', 
'\t', '\t', '<w>', 'print', 'Word', '</w>', '(', '"', '\t', '.', '.', '.', '\t', '<w>', 'Ü', 'ber', 'r', 'as', 'ch', 'ung', '</w>', '"', ')', ';', '\n', 
'\t', '}', '\n', 
'}']
```

**Dataprep** by default does BPE using bpe codes leaned on [the Github Java Corpus](http://groups.inf.ed.ac.uk/cup/javaGithub/). The argument `bpe_codes_id='10k'` tells the **dataprep** tool to use 10,000 bpe merges. 
Other possible values are `1k` and `5k` (1,000 and 5,000 merges respectively). Please refer to section [Learning custom BPE codes](#Learning-custom-BPE-codes) to train custom bpe codes.

**For other commands like `ronin` and `chars`, options `--splt-numbers`, `--stem`, please refer to the [docs](dataprep/cli/spec.py)**.

## Calculate vocabulary 
Set `calc_vocab` param to `True` when calling a preprocessing method to calculate the vocabulary of the preprocessed corpus, e.g.:
```python
>>> import dataprep.api.corpus as pp
>>> pp.basic('/path/to/train/on', calc-vocab=True)
...
Vocab is available at /path/to/vocab
```

## Learning custom BPE codes
If you don't want to use, pre-trained BPE codes, it's possible to train custom ones. For example, to train 10,000 merges on the corpus located at the path `/path/to/train/on`, the following command should be run (only CLI):

```bash
dataprep learn-bpe 10000 -p /path/to/train/on --id custom-bpe-codes 
```

Now it is possible to do bpe splitting by running the bpe command with the number of merges from 0 to 10,000 (for example with 3500 merges):

```bash
dataprep bpe custom-bpe-codes-3500 -p /path/to/preprocess 
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
>>> import dataprep.api.text as pp
>>> input_code = '''void test_WordUeberraschungPrinter() {
...     if (eps >= 0.345e+4) { // FIXME
...         printWord("     ...     Überraschung");
...     }
... }'''
>>> pp.basic(input_code, no_str=True, no_com=True, no_spaces=True, no_unicode=True, no_case=True)
['void', '<w>', 'test', '_', '<Cap>', 'word', '<Cap>', 'ueberraschung', '<Cap>', 'printer', '</w>', '(', ')', '{', 
'if', '(', 'eps', '>', '=', '0', '.', '<w>', '345', 'e', '</w>', '+', '4', ')', '{', '/', '/', '<CAPS>', 'fixme', 
'<w>', 'print', '<Cap>', 'word', '</w>', '(', '"', '.', '.', '.', '<Cap>', '<non-en>', '"', ')', ';', 
'}', 
'}']
```

Similar params can be specified as switches `--no-str`, `--no-com`, `--no-spaces`, `--no-unicode`, `--no-case` in CLI commands.

### Specifying the language
Unless explicitely specified, **dataprep** will try to guess the language of the code to be preprocessed. To make sure the input is preprocessed as intended, it is always a good idea to specify it:
```python
import dataprep.api.text as pp
>>> pp.bpe("volatile", '1k', extension="py")
['<w>', 'vo', 'l', 'at', 'ile', '</w>']
>>> pp.bpe("volatile", '1k', extension="java")
['volatile']
# Since 'volatile' is a keyword in java, it is represented as one token unlike in python 
# where it is pretty rare when used as an identifier and therefore represented as multiple subtokens.
```

When preprocessing a corpus, `dateprep` identifies the language based on the file extension. If you want only files with (a) certain extension(s) to be preprocessed, you can specify --ext param 
```bash
dataprep basic --path /path/to/be/preprocessed --ext "java"

# or if you want to pre-process multiple types of files: 
dataprep basic --path /path/to/be/preprocessed --ext "java|c|py|js"
```
### Miscellaneous
You can specify the path to where the preprocessed corpus will be written:
```bash
dataprep basic --path /path/to/preprocess --output-path /path/to/output
```

To print logs with log level DEBUG and higher to stdout:
```bash
dataprep basic --path /path/to/preprocess --verbose
```

## Getting Help
To get help on commands and options:

```bash
dataprep --help
```


# Advanced

### Caching

When preprocessing a dataset, **dataprep** first parses source code and converts it into internal representation, 
which is after that converted to a preprocessed dataset depending on provided parameters. The intermediate 
representation is cached, so that when the same dataset is pre-processed again with different parameters,
**dataprep** (providing no changes have been made to the dataset) would use the cache rather than parsing 
the source code again.

To store the cache, **dataprep** uses a directory speecified by `$XDG_CACHE_HOME/dataprep/<dataprep_version>` variable if its value is set, 
`$HOME/.cache/dataprep/<dataprep_version>` otherwise.

Removing the cache will not change the final result, however, will result in slower pre-processing.
