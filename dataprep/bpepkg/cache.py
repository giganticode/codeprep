from dataprep.util import to_literal_str, to_non_literal_str

KEY_VALUE_DELIM = '\t'
VALUE_PARTS_DELIM = ' '


def read_bpe_cache(file: str):
    words = {}
    with open(file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            splits = line.split(KEY_VALUE_DELIM)
            second_column = to_non_literal_string(splits[1]).split(VALUE_PARTS_DELIM)
            words[to_non_litetal_str(splits[0])] = second_column
    return words


def dump_bpe_cache(dct, file):
    with open(file, 'w') as f:
        for word, subwords in dct.items():
            f.write(f'{to_literal_str(str(word))}{KEY_VALUE_DELIM}{to_literal_str(" ".join(subwords))}\n')
