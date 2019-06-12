import unittest

from dataprep.bpepkg.merge import MergeList, Merge
from dataprep.model.containers import SplitContainer, OneLineComment, MultilineComment, StringLiteral
from dataprep.model.metadata import PreprocessingMetadata
from dataprep.model.noneng import NonEng
from dataprep.model.numeric import Number
from dataprep.model.placeholders import placeholders
from dataprep.model.whitespace import NewLine, Tab
from dataprep.model.word import Word, Underscore
from dataprep.prepconfig import PrepParam, PrepConfig
from dataprep.split.ngram import NgramSplittingType, NgramSplitConfig
from dataprep.to_repr import to_repr

pl = placeholders

tokens = [
    Number([1, '.', 1]),
    "*",
    SplitContainer([NonEng(Word.from_("übersetzen"))]),
    StringLiteral([
        '"',
        SplitContainer([
            Word.from_("A"),
            NonEng(Word.from_("Wirklich"))
        ]),
        '"'
    ]),
    NewLine(),
    MultilineComment(['/', '*']),
    MultilineComment([
        SplitContainer([NonEng(Word.from_('ц'))]),
        SplitContainer([
            NonEng(Word.from_("blanco")),
            Underscore(),
            Word.from_("english")
        ]),
    ]),
    MultilineComment(['*', '/']),
    NewLine(), Tab(),
    OneLineComment(['/', '/',
        SplitContainer([
            NonEng(Word.from_("DIESELBE")),
            Word.from_("8")
        ])
    ])
]


class ReprTest(unittest.TestCase):

    def test_both_enonly_and_nosplit(self):
        with self.assertRaises(ValueError):
            prep_config = PrepConfig({
                PrepParam.EN_ONLY: 1,
                PrepParam.COM_STR: 0,
                PrepParam.SPLIT: 0,
                PrepParam.TABS_NEWLINES: 1,
                PrepParam.CAPS: 1
            })
            to_repr(prep_config, [], NgramSplitConfig())

    def test_to_repr_0(self):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })

        actual, actual_metadata = to_repr(prep_config, tokens, NgramSplitConfig())

        expected = [
            '1.1',
            "*",
            'übersetzen',
            '"', 'AWirklich', '"',
            '/', '*', 'ц', 'blanco_english', '*', '/',
            '/', '/', "DIESELBE8", pl['olc_end']
        ]
        expected_metadata = PreprocessingMetadata({'*', '"', "*", "/"})

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, actual_metadata)

    ############################################################################################
    ############################################################################################

    def test_to_repr_1_nosep(self):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 1,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })

        actual, actual_metadata = to_repr(prep_config, tokens, NgramSplitConfig())

        expected = [
            '1.1',
            "*",
            pl['non_eng'],
            '"', pl['word_start'], pl['capitals'], 'a',
            pl["capital"], pl['non_eng'], pl['word_end'], '"',
            '/', '*', pl['non_eng'], pl['word_start'], pl['non_eng'],
            '_', 'english', pl['word_end'], '*', '/',
            '/', '/', pl['word_start'], pl['capitals'], pl['non_eng'],
            '8', pl['word_end'], pl['olc_end']
        ]

        expected_metadata = PreprocessingMetadata({'*', '"', "/", "*"})

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, actual_metadata)

    ############################################################################################
    ############################################################################################

    def test_to_repr_2_nosep(self):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 1,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 2,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })

        ngramSplittingConfig = NgramSplitConfig(splitting_type=NgramSplittingType.ONLY_NUMBERS)

        actual, actual_metadata = to_repr(prep_config, tokens, ngramSplittingConfig)

        expected = [
            pl["word_start"],
            '1',
            '.',
            '1',
            pl['word_end'],
            "*",
            pl['non_eng'],
            '"', pl['word_start'], pl['capitals'], 'a',
            pl["capital"], pl['non_eng'], pl['word_end'], '"',
            '/', '*', pl['non_eng'], pl['word_start'], pl['non_eng'],
            '_', 'english', pl['word_end'], '*', '/',
            '/', '/', pl["word_start"], pl['capitals'], pl['non_eng'],
            "8", pl['word_end'], pl['olc_end']
        ]

        expected_metadata = PreprocessingMetadata({'*', '"', "/", "*"})

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, actual_metadata)

    ############################################################################################
    ############################################################################################

    def test_to_repr_with_enonlycontents(self):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 2,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 2,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })

        ngramSplittingConfig = NgramSplitConfig(splitting_type=NgramSplittingType.ONLY_NUMBERS)

        tokens = [
            Number([1, '.', 1]),
            "*",
            SplitContainer([NonEng(Word.from_("dinero"))]),
            StringLiteral([
                '"',
                NonEng(Word.from_("ich")),
                NonEng(Word.from_("weiss")),
                NonEng(Word.from_("nicht")),
                NonEng(Word.from_("was")),
                NonEng(Word.from_("soll")),
                NonEng(Word.from_("es")),
                NonEng(Word.from_("bedeuten")),
                NonEng(Word.from_("dass")),
                NonEng(Word.from_("ich")),
                NonEng(Word.from_("so")),
                NonEng(Word.from_("traurig")),
                NonEng(Word.from_("bin")),
                '"',
            ]),
            NewLine(),
            MultilineComment(['/', '*']),
            MultilineComment([
                SplitContainer([NonEng(Word.from_('ц'))]),
                SplitContainer([
                    NonEng(Word.from_("blanco")),
                    Underscore(),
                    Word.from_("english")
                ]),
            ]),
            MultilineComment(['*', '/']),
            NewLine(), Tab(),
            OneLineComment(['/', '/',
                SplitContainer([
                    NonEng(Word.from_("DIESELBE")),
                    Word.from_("8")
                ])
            ])
        ]

        actual, actual_metadata = to_repr(prep_config, tokens, ngramSplittingConfig)

        expected = [
            pl['word_start'],
            '1',
            '.',
            '1',
            pl['word_end'],
            "*",
            pl['non_eng'],
            '"', pl["non_eng_content"], '"',
            '/', '*', pl['non_eng'],
            pl['word_start'], pl['non_eng'], '_',
            'english', pl['word_end'],
            '*', '/',
            '/', '/', pl['word_start'], pl['capitals'], pl['non_eng'], "8", pl['word_end'],
            pl['olc_end']
        ]

        expected_metadata = PreprocessingMetadata({'*', "/"})

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, actual_metadata)

    def test_to_repr_with_enonlycontents1(self):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 1,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 2,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })

        ngramSplittingConfig = NgramSplitConfig(splitting_type=NgramSplittingType.ONLY_NUMBERS)

        tokens = [
            Number([1, '.', 1]),
            "*",
            SplitContainer([NonEng(Word.from_("dinero"))]),
            StringLiteral([
                '"',
                NonEng(Word.from_("ich")),
                NonEng(Word.from_("weiss")),
                NonEng(Word.from_("nicht")),
                NonEng(Word.from_("was")),
                NonEng(Word.from_("soll")),
                NonEng(Word.from_("es")),
                NonEng(Word.from_("bedeuten")),
                NonEng(Word.from_("dass")),
                NonEng(Word.from_("ich")),
                NonEng(Word.from_("so")),
                NonEng(Word.from_("traurig")),
                NonEng(Word.from_("bin")),
                '"',
            ]),
            NewLine(),
            MultilineComment(['/', '*']),
            MultilineComment([
                SplitContainer([NonEng(Word.from_('ц'))]),
                SplitContainer([
                    NonEng(Word.from_("blanco")),
                    Underscore(),
                    Word.from_("english")
                ]),
            ]),
            MultilineComment(['*', '/']),
            NewLine(), Tab(),
            OneLineComment(['/', '/',
                SplitContainer([
                    NonEng(Word.from_("DIESELBE")),
                    Word.from_("8")
                ])
            ])
        ]

        actual, actual_metadata = to_repr(prep_config, tokens, ngramSplittingConfig)

        expected = [
            pl['word_start'],
            '1',
            '.',
            '1',
            pl['word_end'],
            "*",
            pl['non_eng'],
            '"', pl["non_eng"], pl["non_eng"], pl["non_eng"], pl["non_eng"], pl["non_eng"], pl["non_eng"],
            pl["non_eng"], pl["non_eng"], pl["non_eng"], pl["non_eng"], pl["non_eng"], pl["non_eng"], '"',
            '/', '*', pl['non_eng'],
            pl['word_start'], pl['non_eng'], '_',
            'english', pl['word_end'],
            '*', '/',
            '/', '/', pl['word_start'], pl['capitals'], pl['non_eng'], "8", pl['word_end'],
            pl['olc_end']
        ]

        expected_metadata = PreprocessingMetadata({'*', '"', "/", "*"})

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, actual_metadata)

    ############################################################################################
    ############################################################################################

    def test_to_repr_with_non_eng(self):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 2,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })

        ngramSplittingConfig = NgramSplitConfig(splitting_type=NgramSplittingType.ONLY_NUMBERS)

        actual, actual_metadata = to_repr(prep_config, tokens, ngramSplittingConfig)

        expected = [
            pl['word_start'],
            '1',
            '.',
            '1',
            pl['word_end'],
            "*",
            'übersetzen',
            '"', pl['word_start'], pl['capitals'], 'a', pl['capital'], 'wirklich', pl['word_end'], '"',
            '/', '*', 'ц', pl['word_start'], 'blanco', '_', 'english', pl['word_end'], '*', '/',
            '/', '/', pl['word_start'], pl['capitals'], 'dieselbe', "8", pl['word_end'], pl['olc_end']
        ]

        expected_metadata = PreprocessingMetadata({'*', '"', "/"})

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, actual_metadata)

    #
    #     ############################################################################################
    #     ############################################################################################
    #
    def test_to_repr_with_newlines_and_tabs(self):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 1,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 2,
            PrepParam.TABS_NEWLINES: 0,
            PrepParam.CAPS: 1
        })

        ngramSplittingConfig = NgramSplitConfig(splitting_type=NgramSplittingType.ONLY_NUMBERS,
                                                )

        actual, actual_metadata = to_repr(prep_config, tokens, ngramSplittingConfig)

        expected = [
            pl['word_start'],
            '1',
            '.',
            '1',
            pl['word_end'],
            "*",
            pl['non_eng'],
            '"', pl["word_start"], pl['capitals'], 'a',
            pl["capital"], pl['non_eng'], pl['word_end'], '"',
            '\n',
            '/', '*', pl['non_eng'], pl["word_start"], pl['non_eng'],
            "_", 'english', pl['word_end'], '*', '/',
            '\n', '\t',
            '/', '/', pl["word_start"], pl['capitals'], pl['non_eng'],
            "8", pl['word_end'], pl['olc_end']
        ]

        expected_metadata = PreprocessingMetadata({'*', '"', "/", '\n', '\t'})

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, actual_metadata)

    #
    #     ############################################################################################
    #     ############################################################################################
    #
    def test_to_repr_no_str_no_com(self):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 1,
            PrepParam.COM_STR: 2,
            PrepParam.SPLIT: 2,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })

        ngramSplittingConfig = NgramSplitConfig(splitting_type=NgramSplittingType.ONLY_NUMBERS)

        actual, actual_metadata = to_repr(prep_config, tokens, ngramSplittingConfig)

        expected = [
            pl['word_start'],
            '1',
            '.',
            '1',
            pl['word_end'],
            "*",
            pl['non_eng'],
            pl["string_literal"],
            pl["comment"],
            pl["comment"],
            pl["comment"],
            pl["comment"]
        ]

        expected_metadata = PreprocessingMetadata({'*'})

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, actual_metadata)

    #
    #     ############################################################################################
    #     ############################################################################################
    #
    def test_to_repr_no_nosep(self):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 1,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 2,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })

        ngramSplittingConfig = NgramSplitConfig(splitting_type=NgramSplittingType.ONLY_NUMBERS)

        actual, actual_metadata = to_repr(prep_config, tokens, ngramSplittingConfig)

        expected = [
            pl['word_start'],
            '1',
            '.',
            '1',
            pl['word_end'],
            "*",
            pl['non_eng'],
            '"', pl['word_start'], pl['capitals'], 'a', pl["capital"], pl['non_eng'], pl['word_end'], '"',
            '/', '*', pl['non_eng'], pl['word_start'], pl['non_eng'], '_', 'english', pl['word_end'], '*', '/',
            '/', '/', pl['word_start'], pl['capitals'], pl['non_eng'], "8", pl['word_end'],
            pl['olc_end']
        ]

        expected_metadata = PreprocessingMetadata({'*', '"', "/"})

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, actual_metadata)

    #
    #     ############################################################################################
    #     ############################################################################################
    #
    def test_to_repr_no_no_sep_with_bpe_no_merges(self):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 1,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 4,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })

        ngramSplittingConfig = NgramSplitConfig(splitting_type=NgramSplittingType.BPE,
                                                merges=MergeList(), merges_cache={})

        actual, actual_metadata = to_repr(prep_config, tokens, ngramSplittingConfig)

        expected = [
            pl['word_start'],
            '1',
            '.',
            '1',
            pl['word_end'],
            "*",
            pl['non_eng'],
            '"', pl['word_start'], pl['capitals'], 'a', pl["capital"], pl['non_eng'], pl['word_end'], '"',
            '/', '*', pl['non_eng'], pl['word_start'], pl['non_eng'], '_', 'e', 'n', 'g', 'l', 'i', 's', 'h',
            pl['word_end'], '*', '/',
            '/', '/', pl['word_start'], pl['capitals'], pl['non_eng'], "8", pl['word_end'],
            pl['olc_end']
        ]

        expected_metadata = PreprocessingMetadata({'*', '"', "/", "*"})

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, actual_metadata)

    #
    # #################################################
    # ###   Only tests with single word go below
    # #################################################
    #
    def test_1(self):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 4,
            PrepParam.TABS_NEWLINES: 0,
            PrepParam.CAPS: 1
        })

        ngramSplittingConfig = NgramSplitConfig(splitting_type=NgramSplittingType.BPE,
                                                merges_cache={'while': ['while']})

        tokens = [SplitContainer.from_single_token("While")]

        actual, actual_metadata = to_repr(prep_config, tokens, ngramSplittingConfig)

        expected = [pl['capital'], "while", ]

        expected_metadata = PreprocessingMetadata()

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, actual_metadata)

    def test_merges_no_cache(self):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 4,
            PrepParam.TABS_NEWLINES: 0,
            PrepParam.CAPS: 1
        })

        ngramSplittingConfig = NgramSplitConfig(splitting_type=NgramSplittingType.BPE,
                                                merges=MergeList().append(Merge(('w', 'h'), 10)),
                                                merges_cache={})

        tokens = [SplitContainer.from_single_token("While")]

        actual, actual_metadata = to_repr(prep_config, tokens, ngramSplittingConfig)

        expected = [pl['word_start'], pl['capital'], "wh", "i", "l", "e", pl["word_end"]]

        expected_metadata = PreprocessingMetadata()

        self.assertEqual(expected, actual)
        self.assertEqual(expected_metadata, actual_metadata)


if __name__ == '__main__':
    unittest.main()
