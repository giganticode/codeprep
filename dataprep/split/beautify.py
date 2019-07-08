import re

from dataprep.parse.model.placeholders import placeholders, placeholders_beautiful, separators_beautiful

ws = placeholders['word_start']
we = placeholders['word_end']
cap = placeholders['capital']
caps = placeholders['capitals']


def sep_boundaries(m):
    return "".join(m.group(1).split(" "))


def restore_tabs(text: str) -> str:
    for i in range(1, 11):
        text = text.replace('\\t' + str(i), ' ' * 4 * i)
    return text


def restore_words_from_subwords(text: str) -> str:
    text = re.sub(f"{ws} ((?:\S+ )*?){we}", sep_boundaries, text)

    for k, v in separators_beautiful.items():
        text = text.replace(" " + placeholders[k] + " ", v)

    return text


def restore_capitalization(text: str) -> str:
    text = re.sub(placeholders["capital"] + " (\S+)",
                  lambda m: m.group(1).capitalize(), text)
    text = re.sub(f"((?:^| ){ws} (?:(?! we )(?:.* ))?){caps} (.*?)( (?:[0-9]|{we}|{cap}|{caps})(?:$| ))",
                  lambda m: m.group(1) + m.group(2).upper() + m.group(3),
                  text)
    text = re.sub(placeholders["capitals"] + " (\S+)",
                  lambda m: m.group(1).upper(), text)
    return text


def beautify_placeholders(text: str) -> str:
    for k, v in placeholders_beautiful.items():
        text = text.replace(placeholders[k], v)
    return text


def break_lines(text):
    return re.sub(' ?({|}|;|\*/) ?',
                  lambda m: f'{m.group(1)}\n', text)


def beautify_text(text: str) -> str:
    text = restore_capitalization(text)
    text = text.replace('<eos>', '\n')
    text = beautify_placeholders(text)

    text = restore_words_from_subwords(text)
    text = restore_tabs(text)
    text = text.replace(' . ', '.')
    text = break_lines(text)
    return text
