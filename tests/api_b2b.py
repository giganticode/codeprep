import unittest

import dataprep.api.text as api
from dataprep.parse.model.metadata import PreprocessingMetadata
from dataprep.parse.model.placeholders import placeholders

cap = placeholders['capital']
caps = placeholders['capitals']
ws = placeholders['word_start']
we = placeholders['word_end']
ce = placeholders['olc_end']
ne = placeholders['non_eng']
st = placeholders['string_literal']
com = placeholders['comment']

input_text='''void test_WordUeberraschungPrinter() {
    if (eps >= 0.345e+4) { // FIXME
        printWord("     ...     Überraschung");
    }
}'''


class CliTest(unittest.TestCase):
    def test_empty_without_metadata(self):
        self.assertEqual([], api.nosplit(''))
        self.assertEqual([], api.basic(''))
        self.assertEqual([], api.chars(''))
        self.assertEqual([], api.ronin(''))
        self.assertEqual([], api.bpe('', '1k'))

    def test_create_prep_config_00010(self):
        actual, metadata = api.nosplit(input_text, "java", no_spaces=True, return_metadata=True)

        expected = ['void', 'test_WordUeberraschungPrinter', '(', ')', '{',
                    'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', 'FIXME', ce,
                    'printWord', '(', '"', '.', '.', '.', 'Überraschung', '"', ')', ';',
                    '}',
                    '}'
        ]

        expected_metadata = PreprocessingMetadata(
            nonprocessable_tokens={'void', '(', ')', '{', 'if', '>', '=', '/', '"', '.', '}', ';'},
            word_boundaries=list(range(len(expected)+1)))

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, metadata)

    def test_create_prep_config_3x0xx(self):
        actual = api.nosplit(input_text, "java", no_spaces=True, no_unicode=True)

        expected = ['void', 'test_WordUeberraschungPrinter', '(', ')', '{',
                    'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', 'FIXME', ce,
                    'printWord', '(', '"', '.', '.', '.', ne, '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_x20xx(self):
        actual, metadata = api.nosplit(input_text, "java", no_spaces=True, no_str=True, no_com=True, return_metadata=True)

        expected = ['void', 'test_WordUeberraschungPrinter', '(', ')', '{',
                    'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', com,
                    'printWord', '(', st, ')', ';',
                    '}',
                    '}'
        ]

        expected_metadata = PreprocessingMetadata(
            nonprocessable_tokens={'void', '(', ')', '{', 'if', '>', '=', '}', ';'},
            word_boundaries=list(range(len(expected)+1)))

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, metadata)

    def test_create_prep_config_xx00x(self):
        actual, metadata = api.nosplit(input_text, "java", return_metadata=True)

        expected = ['void', 'test_WordUeberraschungPrinter', '(', ')', '{', '\n',
                    '\t', 'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', 'FIXME', '\n', placeholders['olc_end'],
                    '\t', '\t', 'printWord', '(', '"', '\t', '.', '.', '.', '\t', 'Überraschung', '"', ')', ';', '\n',
                    '\t', '}', '\n',
                    '}'
        ]

        expected_metadata = PreprocessingMetadata(
            nonprocessable_tokens={'void', '(', ')', '{', 'if', '>', '=', '/', '"', '.', '}', ';', '\n', '\t'},
            word_boundaries=list(range(len(expected)+1)))

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, metadata)

    def test_create_prep_config_xx0x1(self):
        with self.assertRaises(TypeError) as context:
            api.nosplit(input_text, "java", no_spaces=True, no_case=True)

    def test_create_prep_config_00111(self):
        actual, metadata = api.basic(input_text, "java", no_spaces=True, no_case=True, return_metadata=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', caps, 'fixme', ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', cap, 'überraschung', '"', ')', ';',
                    '}',
                    '}'
        ]

        expected_metadata = PreprocessingMetadata(
            nonprocessable_tokens={'void', '(', ')', '{', 'if', '>', '=', '/', '"', '.', '}', ';'},
            word_boundaries=[0, 1, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 32, 33,
                             34, 35, 36, 37, 39, 40, 41, 42, 43, 44])

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, metadata)

    def test_create_prep_config_3x1xx(self):
        actual = api.basic(input_text, "java", no_spaces=True, no_case=True, no_unicode=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', caps, 'fixme', ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', ne, '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_x11xx(self):
        actual = api.basic(input_text, "java", no_spaces=True, no_case=True, no_str=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', caps, 'fixme', ce,
                    ws, 'print', cap, 'word', we, '(', st, ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_x21xx(self):
        actual = api.basic(input_text, "java", no_spaces=True, no_case=True, no_str=True, no_com=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', com,
                    ws, 'print', cap, 'word', we, '(', st, ')', ';',
                    '}',
                    '}',
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_x31xx(self):
        actual = api.basic(input_text, "java", no_spaces=True, no_case=True, no_com=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', com,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', cap,  'überraschung', '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_012xx(self):
        actual = api.basic(input_text, "java", no_spaces=True, no_case=True, split_numbers=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>', '=', ws, '0',  '.', '3', '4', '5', 'e', '+', '4', we, ')', '{', '/', '/', caps, 'fixme', ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', cap,  'überraschung', '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_01sxx(self):
        actual = api.basic(input_text, "java", no_spaces=True, stem=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'ep', '>', '=', ws, '0',  '.', '3', '4', '5', 'e', '+', '4', we, ')', '{', '/', '/', caps, 'fixm', ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', cap,  'überraschung', '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_014xx(self):
        actual = api.bpe(input_text, '5k', "java", no_spaces=True, no_case=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ue', 'b', 'err', 'as', 'ch', 'un', 'g', cap, 'printer', we, '(', ')', '{',
                    'if', '(', ws, 'ep', 's', we, '>', '=', ws, '0.', '34', '5', 'e+', '4', we, ')', '{', '/', '/', ws, caps, 'fix', 'me', we, ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', ws, cap, 'ü', 'b', 'err', 'as', 'ch', 'un', 'g', we, '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_015xx(self):
        actual = api.bpe(input_text, '1k', "java", no_spaces=True, no_case=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ue', 'b', 'err', 'as', 'ch', 'un', 'g', cap, 'pr', 'inter', we, '(', ')', '{',
                    'if', '(', ws, 'ep', 's', we, '>','=', ws, '0', '.', '3', '4', '5', 'e', '+', '4', we, ')', '{', '/', '/', ws, caps, 'fix', 'me', we, ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', ws, cap, 'ü', 'b', 'err', 'as', 'ch', 'un', 'g', we, '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_xx6xx(self):
        actual = api.bpe(input_text, '10k', "java", no_spaces=True, no_case=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ue', 'b', 'err', 'as', 'ch', 'ung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>', '=', ws, '0.', '345', 'e+', '4', we, ')', '{', '/', '/', caps, 'fixme', ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', ws, cap, 'ü', 'b', 'err', 'as', 'ch', 'ung', we, '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_xx8xx(self):
        actual, metadata = api.chars(input_text, "java", no_spaces=True, no_case=True, return_metadata=True)

        expected = ['void', ws, 't', 'e', 's', 't', '_', cap, 'w', 'o', 'r', 'd', cap, 'u', 'e', 'b', 'e', 'r', 'r', 'a', 's', 'c', 'h', 'u', 'n', 'g', cap, 'p', 'r', 'i', 'n', 't', 'e', 'r', we, '(', ')', '{',
                    'if', '(', ws, 'e', 'p', 's', we, '>','=', ws, '0', '.', '3', '4', '5', 'e', '+', '4', we, ')', '{', '/', '/', ws, caps, 'f', 'i', 'x', 'm', 'e', we, ce,
                    ws, 'p', 'r', 'i', 'n', 't', cap, 'w', 'o', 'r', 'd', we, '(', '"', '.', '.', '.', ws, cap, 'ü', 'b', 'e', 'r', 'r', 'a', 's', 'c', 'h', 'u', 'n', 'g', we, '"', ')', ';',
                    '}',
                    '}'
        ]

        expected_metadata = PreprocessingMetadata(
            nonprocessable_tokens={'void', '(', ')', '{', 'if', '>', '=', '/', '"', '.', '}', ';'},
            word_boundaries=[0, 1, 35, 36, 37, 38, 39, 40, 45, 46, 47, 57, 58, 59, 60, 61, 69, 70, 82, 83, 84, 85, 86, 87, 102, 103, 104, 105, 106, 107])

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, metadata)

    def test_create_prep_config_xx10x(self):
        actual = api.basic(input_text, "java", no_case=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{', '\n',
                    '\t', 'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', caps, 'fixme', '\n', ce,
                    '\t', '\t', ws, 'print', cap, 'word', we, '(', '"', '\t', '.', '.', '.', '\t', cap, 'überraschung', '"', ')', ';', '\n',
                    '\t', '}', '\n'
                    , '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_xx1x1(self):
        actual = api.basic(input_text, "java", no_spaces=True)

        expected = ['void', ws, 'test', '_', 'Word', 'Ueberraschung', 'Printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>', '=', '0.345e+4', ')', '{', '/', '/', 'FIXME', ce,
                    ws, 'print', 'Word', we, '(', '"', '.', '.', '.', 'Überraschung', '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_00300(self):
        actual = api.ronin(input_text, "java")

        expected = ['void', ws, 'test', 'Word', 'Ueberraschung', 'Printer', we, '(', ')', '{',  '\n',
                    '\t', 'if', '(', 'eps', '>', '=', ws ,'0', '.', '3', '4', '5', 'e', '+', '4', we, ')', '{', '/', '/', ws, 'FIX', 'ME', we, '\n', ce,
                    '\t', '\t', ws, 'print', 'Word', we, '(', '"', '\t', '.', '.', '.', '\t', 'Überraschung', '"', ')', ';', '\n',
                    '\t', '}', '\n',
                    '}'
        ]

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
