placeholders = {
    'comment': '<comment>',
    'string_literal': '<str_literal>',
    'identifier': '<identifier>',
    'word_start': '`w',
    'word_end': 'w`',
    'capital': '`C',
    'capitals': '`Cs',
    'var': '<var>',
    'string_resource': '<str_res>',
    'ect': '``',
    'non_eng': '`E',
    'non_eng_content': '`Es',
    'log_statement': '`L',
    'log_statement_end': 'L`',
    'loggable_block': '`l',
    'loggable_block_end': 'l`',
    'pad_token': '<pad>',
    'olc_end': 'm`',
    'trace': '`trace',
    'debug': '`debug',
    'info': '`info',
    'warn': '`warn',
    'error': '`error',
    'fatal': '`fatal',
    'unknown': '`unknown'
}

placeholders_beautiful = {
    'comment': '<comment>',
    'string_literal': '<str_literal>',
    'identifier': '<identifier>',
    'var': '<var>',
    'string_resource': '<str_res>',
    'ect': '\n\n',
    'non_eng': '<non_eng>',
    'non_eng_content': '<non_eng_content>',
    'pad_token': '<pad>'
}

separators_beautiful = {
    'word_end': '',
}

logging_placeholders = [
    placeholders['log_statement'],
    placeholders['log_statement_end'],
    placeholders['loggable_block'],
    placeholders['loggable_block_end'],
    placeholders['trace'],
    placeholders['debug'],
    placeholders['info'],
    placeholders['warn'],
    placeholders['error'],
    placeholders['fatal'],
    placeholders['unknown'],
]
