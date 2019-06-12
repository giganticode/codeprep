KEY_VALUE_DELIM = '\t'
VALUE_PARTS_DELIM = ' '


def read_bpe_cache(file: str):
    words = {}
    with open(file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            splits = line.split(KEY_VALUE_DELIM)
            second_column = splits[1].split(VALUE_PARTS_DELIM)
            words[splits[0]] = second_column
    return words


def dump_bpe_cache(dct, file):
    with open(file, 'w') as f:
        for word, subwords in dct.items():
            f.write(f'{str(word)}{KEY_VALUE_DELIM}{" ".join(subwords)}\n')
