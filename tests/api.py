import unittest

import dataprep
from dataprep.model.placeholders import placeholders

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
    def test_create_prep_config_00010(self):
        actual = dataprep.nosplit(input_text, no_spaces=True)

        expected = ['void', 'test_WordUeberraschungPrinter', '(', ')', '{',
                    'if', '(', 'eps', '>=', '0.345e+4', ')', '{', '//', 'FIXME', ce,
                    'printWord', '(', '"', '.', '.', '.', 'Überraschung', '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_3x0xx(self):
        with self.assertRaises(TypeError) as context:
            dataprep.nosplit(input_text, no_spaces=True, no_unicode=True)

    def test_create_prep_config_x20xx(self):
        actual = dataprep.nosplit(input_text, no_spaces=True, no_str=True, no_com=True)

        expected = ['void', 'test_WordUeberraschungPrinter', '(', ')', '{',
                    'if', '(', 'eps', '>=', '0.345e+4', ')', '{', com,
                    'printWord', '(', st, ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_xx00x(self):
        actual = dataprep.nosplit(input_text)

        expected = ['void', 'test_WordUeberraschungPrinter', '(', ')', '{', '\n',
                    '\t', 'if', '(', 'eps', '>=', '0.345e+4', ')', '{', '//', 'FIXME', placeholders['olc_end'], '\n',
                    '\t', '\t', 'printWord', '(', '"', '\t', '.', '.', '.', '\t', 'Überraschung', '"', ')', ';', '\n',
                    '\t', '}', '\n',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_xx0x1(self):
        with self.assertRaises(TypeError) as context:
            dataprep.nosplit(input_text, no_spaces=True, no_case=True)

    def test_create_prep_config_00111(self):
        actual = dataprep.basic(input_text, no_spaces=True, no_case=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>=', '0.345e+4', ')', '{', '//', caps, 'fixme', ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', cap, 'überraschung', '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_3x1xx(self):
        actual = dataprep.basic(input_text, no_spaces=True, no_case=True, no_unicode=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>=', '0.345e+4', ')', '{', '//', caps, 'fixme', ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', cap, ne, '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_x11xx(self):
        actual = dataprep.basic(input_text, no_spaces=True, no_case=True, no_str=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>=', '0.345e+4', ')', '{', '//', caps, 'fixme', ce,
                    ws, 'print', cap, 'word', we, '(', st, ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_x21xx(self):
        actual = dataprep.basic(input_text, no_spaces=True, no_case=True, no_str=True, no_com=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>=', '0.345e+4', ')', '{', com,
                    ws, 'print', cap, 'word', we, '(', st, ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_x31xx(self):
        actual = dataprep.basic(input_text, no_spaces=True, no_case=True, no_com=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>=', '0.345e+4', ')', '{', com,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', cap,  'überraschung', '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_012xx(self):
        actual = dataprep.basic_with_numbers(input_text, no_spaces=True, no_case=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>=', ws, '0',  '.', '3', '4', '5', 'e', '+', '4', we, ')', '{', '//', caps, 'fixme', ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', cap,  'überraschung', '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_014xx(self):
        actual = dataprep.bpe(input_text, '5k', no_spaces=True, no_case=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ue', 'b', 'err', 'as', 'ch', 'un', 'g', cap, 'printer', we, '(', ')', '{',
                    'if', '(', ws, 'ep', 's', we, '>=', ws, '0.', '34', '5', 'e+', '4', we, ')', '{', '//', ws, caps, 'fix', 'me', we, ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', ws, cap, 'ü', 'b', 'err', 'as', 'ch', 'un', 'g', we, '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_015xx(self):
        actual = dataprep.bpe(input_text, '1k', no_spaces=True, no_case=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ue', 'b', 'err', 'as', 'ch', 'un', 'g', cap, 'pr', 'inter', we, '(', ')', '{',
                    'if', '(', ws, 'ep', 's', we, '>=', ws, '0', '.', '3', '4', '5', 'e', '+', '4', we, ')', '{', '//', ws, caps, 'fix', 'me', we, ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', ws, cap, 'ü', 'b', 'err', 'as', 'ch', 'un', 'g', we, '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_xx6xx(self):
        actual = dataprep.bpe(input_text, '10k', no_spaces=True, no_case=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ue', 'b', 'err', 'as', 'ch', 'ung', cap, 'printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>=', ws, '0.', '345', 'e+', '4', we, ')', '{', '//', caps, 'fixme', ce,
                    ws, 'print', cap, 'word', we, '(', '"', '.', '.', '.', ws, cap, 'ü', 'b', 'err', 'as', 'ch', 'ung', we, '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_xx8xx(self):
        actual = dataprep.chars(input_text, no_spaces=True, no_case=True)

        expected = [ws, 'v', 'o', 'i', 'd', we, ws, 't', 'e', 's', 't', '_', cap, 'w', 'o', 'r', 'd', cap, 'u', 'e', 'b', 'e', 'r', 'r', 'a', 's', 'c', 'h', 'u', 'n', 'g', cap, 'p', 'r', 'i', 'n', 't', 'e', 'r', we, '(', ')', '{',
                    ws, 'i', 'f', we, '(', ws, 'e', 'p', 's', we, '>=', ws, '0', '.', '3', '4', '5', 'e', '+', '4', we, ')', '{', '//', ws, caps, 'f', 'i', 'x', 'm', 'e', we, ce,
                    ws, 'p', 'r', 'i', 'n', 't', cap, 'w', 'o', 'r', 'd', we, '(', '"', '.', '.', '.', ws, cap, 'ü', 'b', 'e', 'r', 'r', 'a', 's', 'c', 'h', 'u', 'n', 'g', we, '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_xx10x(self):
        actual = dataprep.basic(input_text, no_case=True)

        expected = ['void', ws, 'test', '_', cap, 'word', cap, 'ueberraschung', cap, 'printer', we, '(', ')', '{', '\n',
                    '\t', 'if', '(', 'eps', '>=', '0.345e+4', ')', '{', '//', caps, 'fixme', ce, '\n',
                    '\t', '\t', ws, 'print', cap, 'word', we, '(', '"', '\t', '.', '.', '.', '\t', cap, 'überraschung', '"', ')', ';', '\n',
                    '\t', '}', '\n'
                    , '}'
        ]

        self.assertEqual(expected, actual)

    def test_create_prep_config_xx1x1(self):
        actual = dataprep.basic(input_text, no_spaces=True)

        expected = ['void', ws, 'test', '_', 'Word', 'Ueberraschung', 'Printer', we, '(', ')', '{',
                    'if', '(', 'eps', '>=', '0.345e+4', ')', '{', '//', 'FIXME', ce,
                    ws, 'print', 'Word', we, '(', '"', '.', '.', '.', 'Überraschung', '"', ')', ';',
                    '}',
                    '}'
        ]

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
