import unittest

from dataprep.parse.model.numeric import Number

from dataprep.parse.matchers import split_into_words
from dataprep.parse.model.containers import SplitContainer
from dataprep.parse.model.whitespace import NewLine, SpaceInString
from dataprep.parse.model.word import Word, Underscore
from dataprep.parse.subtokens import is_number, split_string


class SplitIntoTokensTest(unittest.TestCase):
    def test_simple(self):
        actual = split_into_words("123\nAb2cd34Ef000GG j_89_J")

        expected = [Number('123'),
                    NewLine(),
                    SplitContainer([Word.from_('Ab'), Word.from_('2'), Word.from_('cd'),
                                    Word.from_('34'), Word.from_('Ef'), Word.from_('000'), Word.from_('GG')]),
                    SplitContainer([Word.from_('j'), Underscore(), Word.from_('89'), Underscore(), Word.from_('J')])]

        self.assertEqual(expected, actual)

class SplitStringTest(unittest.TestCase):
    def test_simple(self):
        actual = split_string("123\nAb2cd34Ef000GG     j_89_J")

        expected = [Number('123'),
                    NewLine(),
                    SplitContainer([Word.from_('Ab'), Word.from_('2'), Word.from_('cd'),
                                    Word.from_('34'), Word.from_('Ef'), Word.from_('000'), Word.from_('GG')]),
                    SpaceInString(5),
                    SplitContainer([Word.from_('j'), Underscore(), Word.from_('89'), Underscore(), Word.from_('J')])]

        self.assertEqual(expected, actual)


class IsNumberTest(unittest.TestCase):
    def test_zero(self):
        self.assertTrue(is_number("0"))

    def test_one_digit_int(self):
        self.assertTrue(is_number("8"))

    def test_negative_int(self):
        self.assertFalse(is_number("-5"))

    def test_int(self):
        self.assertTrue(is_number("23450012"))

    def test_long1(self):
        self.assertTrue(is_number("283463L"))

    def test_long2(self):
        self.assertTrue(is_number("342424242l"))

    def test_double_zero1(self):
        self.assertTrue(is_number("0."))

    def test_double_zero2(self):
        self.assertTrue(is_number(".0"))

    def test_double_zero3(self):
        self.assertTrue(is_number(".0d"))

    def test_double_only_before(self):
        self.assertTrue(is_number("353535."))

    def test_double_only_before2(self):
        self.assertTrue(is_number("353535.D"))

    def test_float_only_after(self):
        self.assertTrue(is_number(".353535F"))

    def test_float(self):
        self.assertTrue(is_number(".353535f"))

    def test_double_scientific(self):
        self.assertTrue(is_number("0.2e+3D"))

    def test_float_scientific_only_before(self):
        self.assertTrue(is_number("23424.E-30F"))

    def test_float_scientific_only_after(self):
        self.assertTrue(is_number(".002e-0f"))

    def test_bin(self):
        self.assertTrue(is_number("0b10101"))

    def test_bin_long(self):
        self.assertTrue(is_number("0b0011L")) # java -- not python

    def test_bin_zero(self):
        self.assertTrue(is_number("0b0"))

    def test_hex(self):
        self.assertTrue(is_number("0x8AbCc006EfBd"))

    def test_hex_wrong_char(self):
        self.assertFalse(is_number("0xG12"))

    def test_hex_long(self):
        self.assertTrue(is_number("0x56DL"))

    def test_hex_long2(self):
        self.assertTrue(is_number("0x56Dl"))


if __name__ == '__main__':
    unittest.main()
