# Dataprep

[![Build Status](https://travis-ci.org/giganticode/dataprep.svg?branch=master)](https://travis-ci.org/giganticode/dataprep)

This is a tool for preprocessing of source code corpora according to specified vocabulary modeling choice.

# Getting started

Make sure you have python >= 3.6 installed in your system.
```bash
python --version
``` 

Make sure pip, setuptools and wheel are up to date.
```bash
python -m pip install --upgrade pip setuptools wheel
```

To install the **dataprep** follow the steps below:
```bash
git clone https://github.com/giganticode/dataprep
cd dataprep
git checkout release-0.1.x
pip install .
```

At this point you should be able to run:
```bash
dataprep --version
>> dataprep 0.1.0-alpha
```

# Usage examples

The tool can be run from command line, as well as from code as a python library. Below we demonstrate how to use it in each scenario.

### CLI

To tokenize the corpus and split camelCase and snake_case words run:

```bash
dataprep --path /path/to/the/dataset basic
```

To tokenize the corpus without splitting any tokens, 
but instead remove string literals and comments, 
and remove all tabs and newlines:

```bash
dataprep --path /path/to/the/dataset --no-str --no-com --no-spaces nosplit
```

To 
1. lowercase all the words in the dataset; 
1. filter out words containing non-ascii characters;
3. camelCase- and snake_case- split; 
4. apply bpe with 5k merges on top;

run:

```bash
dataprep --path /path/to/the/dataset --no-case --no-unicode bpe 5k
```

To convert smaller amount of text, instead of providing a path 
(which is also can be done from the code -- see [API](#API) section) run:

```bash
dataprep "someComplexIdentifier" basic
>> [<word_start>, 'some', 'Complex', 'Identifier', <word_end>]
```
 
To get more information run:

```bash
dataprep --help
```

### API

To tokenize the corpus and split camelCase and snake_case words run:

```python
>>> import dataprep
>>> dataprep.basic('newValue_tmp = "3"  //FIXME')
['<w>', 'new', 'Value', '_', 'tmp', '</w>', '=', '"', '3', '"', '\t', '//', 'FIXME']
```

To tokenize the corpus without splitting any tokens, 
but instead remove string literals and comments, 
and remove all tabs and newlines:

```python
>>> import dataprep
>>> dataprep.nosplit('newValue_tmp = "3"  //FIXME', no_str=True, no_com=True, no_spaces=True)
['newValue_tmp', '=', '<str-literal>', '<comment>']
```

To 
1. lowercase all the words in the dataset; 
1. filter out words containin non-ascii characters;
3. camelCase- and snake_case- split; 
4. apply bpe with 5k merges on top;

run:

```python
>>> import dataprep
>>> dataprep.bpe('newValue_tmp = "3"  //FIXME', '5k', no_case=True, no_unicode=True)
['<w>', 'new', '<Cap>', 'value', '_', 'tmp', '</w>', '=', '"', '3', '"', '//', '<w>', '<CAPS>', 'fix', 'me', '</w>']
```

# Advanced

### Advanced Settings

### Caching

When preprocessing a dataset, **dataprep** first parses source code and converts it into internal representaion, 
which is after that converted to a preprocessed dataset depending on provided parameters. The intermediate 
representation is cached, so that when the same dataset is pre-processed again with different paramaters,
**dataprep** (providing no changes have been made to the dataset) would use the cache rather than parsing 
the source code again.

\<TBD caching of bpe split words>

To store the cache, **dataprep** uses a directory speecified by `$XDG_CACHE_HOME/dataprep/<dataprep_version>` variable if its value is set, 
`$HOME/.cache/dataprep/<dataprep_version>` otherwise.

Removing the cache will not change the final result, however will result in slower pre-processing.

### BPE (Byte-pair encoding)

\<TBD>

### Configuration values for special tokens

\<TBD>

