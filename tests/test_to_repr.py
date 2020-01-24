# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import time

import pytest

from codeprep.bpepkg.bpe_encode import BpeData
from codeprep.bpepkg.merge import MergeList, Merge
from codeprep.tokens.containers import SplitContainer, OneLineComment, MultilineComment, StringLiteral
from codeprep.preprocess.metadata import PreprocessingMetadata
from codeprep.tokens.noneng import NonEng
from codeprep.tokens.numeric import Number
from codeprep.preprocess.placeholders import placeholders
from codeprep.tokens.whitespace import Tab, NewLine, SpaceInString
from codeprep.tokens.word import Word, Underscore, NonCodeChar, Operator
from codeprep.prepconfig import PrepParam, PrepConfig
from codeprep.pipeline.to_repr import to_repr

pl = placeholders
cwe = placeholders['compound_word_end']

tokens = [
    Number('1.1'),
    Operator("*"),
    NonEng(SplitContainer([Word.from_("übersetzen")])),
    StringLiteral([
        NonCodeChar('"'),
        NonEng(
            SplitContainer([
                Word.from_("A"),
                Word.from_("Wirklicä")
            ])
        ),
        SpaceInString(1),
        NonCodeChar('"')
    ], 11),
    NewLine(),
    MultilineComment([NonCodeChar('/'), NonCodeChar('*')]),
    MultilineComment([
        NonEng(
            SplitContainer([Word.from_('ц')]),
        ),
        NonEng(
            SplitContainer([
                Word.from_("blanco"),
                Underscore(),
                Word.from_("english")
            ])
        ),
    ]),
    MultilineComment([NonCodeChar('*'), NonCodeChar('/')]),
    NewLine(), Tab(),
    OneLineComment([NonCodeChar('/'), NonCodeChar('/'),
        NonEng(
            SplitContainer([
                Word.from_("DIESELBE"),
                Word.from_("8")
            ])
        )
    ])
]


def test_both_enonly_and_nosplit():
    with pytest.raises(ValueError):
        prep_config = PrepConfig({
            PrepParam.EN_ONLY: 'U',
            PrepParam.COM: 'c',
            PrepParam.STR: '1',
            PrepParam.SPLIT: '0',
            PrepParam.TABS_NEWLINES: '0',
            PrepParam.CASE: 'l'
        })
        to_repr(prep_config, [], BpeData())


def test_to_repr_0():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    actual, actual_metadata = to_repr(prep_config, tokens)

    expected = [
        '1.1',
        "*",
        'übersetzen',
        '"', 'AWirklicä', '"',
        '/', '*', 'ц', 'blanco_english', '*', '/',
        '/', '/', "DIESELBE8", pl['olc_end']
    ]
    expected_metadata = PreprocessingMetadata({'"', "*", "/"},
                                              word_boundaries=list(range(16+1)),
                                              token_types=[Number, Operator, SplitContainer,
                                                           StringLiteral, StringLiteral, StringLiteral,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           OneLineComment, OneLineComment, OneLineComment, OneLineComment])

    assert expected == actual
    assert expected_metadata == actual_metadata


def test_to_repr_0_max_str_length_7():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '7',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    actual, actual_metadata = to_repr(prep_config, tokens)

    expected = [
        '1.1',
        "*",
        'übersetzen',
        '"', '"',
        '/', '*', 'ц', 'blanco_english', '*', '/',
        '/', '/', "DIESELBE8", pl['olc_end']
    ]
    expected_metadata = PreprocessingMetadata({'"', "*", "/"},
                                              word_boundaries=[0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                                              token_types=[Number, Operator, SplitContainer, StringLiteral,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           OneLineComment, OneLineComment, OneLineComment, OneLineComment])

    assert expected == actual
    assert expected_metadata == actual_metadata


def test_to_repr_0_max_str_length_B():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: 'B',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    actual, actual_metadata = to_repr(prep_config, tokens)

    expected = [
        '1.1',
        "*",
        'übersetzen',
        '"', "AWirklicä", '"',
        '/', '*', 'ц', 'blanco_english', '*', '/',
        '/', '/', "DIESELBE8", pl['olc_end']
    ]
    expected_metadata = PreprocessingMetadata({'"', "*", "/"},
                                              word_boundaries=list(range(16+1)),
                                              token_types=[Number, Operator, SplitContainer,
                                                           StringLiteral, StringLiteral, StringLiteral,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           OneLineComment, OneLineComment, OneLineComment, OneLineComment])

    assert expected == actual
    assert expected_metadata == actual_metadata


def test_to_repr_F():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    actual, actual_metadata = to_repr(prep_config, tokens)

    expected = [
        '1.1',
        "*",
        'übersetzen',
        '"AWirklicä\xa0"',
        '/', '*', 'ц', 'blanco_english', '*', '/',
        '/', '/', "DIESELBE8", pl['olc_end']
    ]
    expected_metadata = PreprocessingMetadata({"*", "/"}, word_boundaries=list(range(14+1)),
                                              token_types=[Number, Operator, SplitContainer, StringLiteral,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           OneLineComment, OneLineComment, OneLineComment, OneLineComment])

    assert expected == actual
    assert expected_metadata == actual_metadata


def test_to_repr_F_max_str_length_7():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '7',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    actual, actual_metadata = to_repr(prep_config, tokens)

    expected = [
        '1.1',
        "*",
        'übersetzen',
        '""',
        '/', '*', 'ц', 'blanco_english', '*', '/',
        '/', '/', "DIESELBE8", pl['olc_end']
    ]
    expected_metadata = PreprocessingMetadata({"*", "/"},
                                              word_boundaries=list(range(14+1)),
                                              token_types=[Number, Operator, SplitContainer, StringLiteral,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           OneLineComment, OneLineComment, OneLineComment, OneLineComment])

    assert expected == actual
    assert expected_metadata == actual_metadata


def test_to_repr_F_max_str_length_B():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: 'B',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    actual, actual_metadata = to_repr(prep_config, tokens)

    expected = [
        '1.1',
        "*",
        'übersetzen',
        '"AWirklicä\xa0"',
        '/', '*', 'ц', 'blanco_english', '*', '/',
        '/', '/', "DIESELBE8", pl['olc_end']
    ]
    expected_metadata = PreprocessingMetadata({"*", "/"}, word_boundaries=list(range(14+1)),
                                              token_types=[Number, Operator, SplitContainer, StringLiteral,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           OneLineComment, OneLineComment, OneLineComment, OneLineComment])

    assert expected == actual
    assert expected_metadata == actual_metadata

############################################################################################
############################################################################################


def test_to_repr_1_nosep():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '1',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })

    actual, actual_metadata = to_repr(prep_config, tokens)

    expected = [
        '1.1',
        "*",
        pl['non_eng'],
        '"',
        pl['non_eng'], '"',
        '/', '*', pl['non_eng'], pl['non_eng'], '*', '/',
        '/', '/', pl['non_eng'],
        pl['olc_end']
    ]

    expected_metadata = PreprocessingMetadata({'*', '"', "/", "*"},
                                              word_boundaries=list(range(16+1)),
                                              token_types=[Number, Operator, NonEng,
                                                           StringLiteral, StringLiteral, StringLiteral,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           OneLineComment, OneLineComment, OneLineComment, OneLineComment])

    assert expected == actual
    assert expected_metadata == actual_metadata

############################################################################################
############################################################################################


def test_to_repr_2_nosep():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '2',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })

    actual, actual_metadata = to_repr(prep_config, tokens)

    expected = [
        pl["word_start"],
        '1',
        '.',
        '1',
        pl['word_end'],
        "*",
        pl['non_eng'],
        '"', pl['non_eng'], '"',
        '/', '*', pl['non_eng'], pl['non_eng'], '*', '/',
        '/', '/', pl['non_eng'], pl['olc_end']
    ]

    expected_metadata = PreprocessingMetadata({'*', '"', "/", "*"},
                                              word_boundaries=[0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                                              token_types=[Number, Operator, NonEng,
                                                           StringLiteral, StringLiteral, StringLiteral,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           OneLineComment, OneLineComment, OneLineComment, OneLineComment])

    assert expected == actual
    assert expected_metadata == actual_metadata

############################################################################################
############################################################################################


def test_to_repr_with_enonlycontents1():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '2',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })

    tokens = [
        Number("1.1"),
        Operator("*"),
        NonEng(SplitContainer([Word.from_("dinero")])),
        StringLiteral([
            NonCodeChar('"'),
            NonEng(SplitContainer([Word.from_("ich")])),
            SpaceInString(),
            NonEng(SplitContainer([Word.from_("weiss")])),
            SpaceInString(),
            NonEng(SplitContainer([Word.from_("nicht")])),
            SpaceInString(),
            NonEng(SplitContainer([Word.from_("was")])),
            SpaceInString(),
            NonEng(SplitContainer([Word.from_("soll")])),
            SpaceInString(),
            NonEng(SplitContainer([Word.from_("es")])),
            SpaceInString(),
            NonEng(SplitContainer([Word.from_("bedeuten")])),
            SpaceInString(),
            NonEng(SplitContainer([Word.from_("dass")])),
            SpaceInString(),
            NonEng(SplitContainer([Word.from_("ich")])),
            SpaceInString(),
            NonEng(SplitContainer([Word.from_("so")])),
            SpaceInString(),
            NonEng(SplitContainer([Word.from_("traurig")])),
            SpaceInString(),
            NonEng(SplitContainer([Word.from_("bin")])),
            NonCodeChar('"'),
        ], 62),
        NewLine(),
        MultilineComment([NonCodeChar('/'), NonCodeChar('*')]),
        MultilineComment([
            NonEng(SplitContainer([Word.from_('ц')])),
            NonEng(
                SplitContainer([
                    Word.from_("blanco"),
                    Underscore(),
                    Word.from_("english")
                ])
            ),
        ]),
        MultilineComment([NonCodeChar('*'), NonCodeChar('/')]),
        NewLine(), Tab(),
        OneLineComment([NonCodeChar('/'), NonCodeChar('/'),
            NonEng(
                SplitContainer([
                    Word.from_("DIESELBE"),
                    Word.from_("8")
                ])
            )
        ])
    ]

    actual, actual_metadata = to_repr(prep_config, tokens)

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
        '/', '*', pl['non_eng'], pl['non_eng'],
        '*', '/',
        '/', '/',  pl['non_eng'],
        pl['olc_end']
    ]

    expected_metadata = PreprocessingMetadata({'*', '"', "/", "*"},
                                              word_boundaries=[0] + list(range(5, 32)),
                                              token_types=[Number, Operator, NonEng]
                                                          + [StringLiteral] * 14
                                                          + [MultilineComment] * 6
                                                          + [OneLineComment] * 4)

    assert expected == actual
    assert expected_metadata == actual_metadata

############################################################################################
############################################################################################


def test_to_repr_with_non_eng():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '2',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })

    actual, actual_metadata = to_repr(prep_config, tokens)

    expected = [
        pl['word_start'],
        '1',
        '.',
        '1',
        pl['word_end'],
        "*",
        'übersetzen',
        '"', pl['word_start'], pl['capitals'], 'a', pl['capital'], 'wirklicä', pl['word_end'], '"',
        '/', '*', 'ц', pl['word_start'], 'blanco', '_', 'english', pl['word_end'], '*', '/',
        '/', '/', pl['word_start'], pl['capitals'], 'dieselbe', "8", pl['word_end'], pl['olc_end']
    ]

    expected_metadata = PreprocessingMetadata({'*', '"', "/"}, word_boundaries=[0, 5, 6, 7, 8, 14, 15, 16, 17, 18,
                                                                                23, 24, 25, 26, 27, 32, 33],
                                              token_types=[Number, Operator, SplitContainer]
                                                          + [StringLiteral] * 3
                                                          + [MultilineComment] * 6
                                                          + [OneLineComment] * 4)

    assert expected == actual
    assert expected_metadata == actual_metadata

#
#     ############################################################################################
#     ############################################################################################
#


def test_to_repr_with_newlines_and_tabs():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '2',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'l'
    })

    actual, actual_metadata = to_repr(prep_config, tokens)

    expected = [
        pl['word_start'],
        '1',
        '.',
        '1',
        pl['word_end'],
        "*",
        pl['non_eng'],
        '"', pl['non_eng'], '"',
        '\n',
        '/', '*', pl['non_eng'], pl['non_eng'], '*', '/',
        '\n', '\t',
        '/', '/', pl['non_eng'], pl['olc_end']
    ]

    expected_metadata = PreprocessingMetadata({'*', '"', "/", '\n', '\t'},
                                              word_boundaries=[0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
                                              token_types=[Number, Operator, NonEng]
                                                          + [StringLiteral] * 3 + [NewLine]
                                                          + [MultilineComment] * 6 + [NewLine, Tab]
                                                          + [OneLineComment] * 4)

    assert expected == actual
    assert expected_metadata == actual_metadata

#
#     ############################################################################################
#     ############################################################################################
#

def test_to_repr_no_str_no_com():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: '0',
        PrepParam.STR: '0',
        PrepParam.SPLIT: '2',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })

    actual, actual_metadata = to_repr(prep_config, tokens)

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

    expected_metadata = PreprocessingMetadata({'*'}, word_boundaries=[0, 5, 6, 7, 8, 9, 10, 11, 12],
                                              token_types=[Number, Operator, NonEng, StringLiteral,
                                                           MultilineComment, MultilineComment, MultilineComment, OneLineComment])

    assert expected == actual
    assert expected_metadata == actual_metadata

#
#     ############################################################################################
#     ############################################################################################
#

def test_to_repr_no_nosep():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '2',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'l'
    })

    actual, actual_metadata = to_repr(prep_config, tokens)

    expected = [
        pl['word_start'],
        '1',
        '.',
        '1',
        pl['word_end'],
        "*",
        pl['non_eng'],
        '"', pl['non_eng'], '"',
        '/', '*', pl['non_eng'], pl['non_eng'], '*', '/',
        '/', '/', pl['non_eng'],
        pl['olc_end']
    ]

    expected_metadata = PreprocessingMetadata({'*', '"', "/"},
                                              word_boundaries=[0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                                              token_types=[Number, Operator, NonEng]
                                                          + [StringLiteral] * 3
                                                          + [MultilineComment] * 6
                                                          + [OneLineComment] * 4)

    assert expected == actual
    assert expected_metadata == actual_metadata


def test_to_repr_no_no_sep_with_bpe_no_merges():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '4',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    actual, actual_metadata = to_repr(prep_config, tokens, BpeData(merges_cache={}, merges=MergeList()))

    expected = [
        '1',
        '.',
        '1',
        cwe,
        "*" + cwe,
        '÷', 'b', 'e', 'r', 's', 'e', 't', 'z', 'e', 'n', '</t>',
        '"', 'A', 'W', 'i', 'r', 'k', 'l', 'i', 'c', '\xf7', '\xa0', '"', cwe,
        '/' + cwe, '*' + cwe, '\xf7', cwe, 'b', 'l', 'a', 'n', 'c', 'o', '_', 'e', 'n', 'g', 'l', 'i', 's', 'h', cwe, '*' + cwe, '/' + cwe,
        '/' + cwe, '/' + cwe, 'D', 'I', 'E', 'S', 'E', 'L', 'B', 'E', '8', cwe,
        pl['olc_end'] + cwe
    ]

    assert expected == actual


# def test_to_repr_ronin():
#     prep_config = PrepConfig({
#         PrepParam.EN_ONLY: 'U',
#         PrepParam.COM: 'c',
#         PrepParam.STR: '1',
#         PrepParam.SPLIT: '3',
#         PrepParam.TABS_NEWLINES: '0',
#         PrepParam.CASE: 'u'
#     })
#
#     actual, actual_metadata = to_repr(prep_config, tokens, BpeData(merges_cache={}, merges=MergeList()))
#
#     expected = [
#         pl['word_start'],
#         '1',
#         '.',
#         '1',
#         pl['word_end'],
#         "*",
#         pl['non_eng'],
#         '"', pl['non_eng'], '"',
#         '/', '*', pl['non_eng'], pl['non_eng'], '*', '/',
#         '/', '/', pl['non_eng'],
#         pl['olc_end']
#     ]
#
#     expected_metadata = PreprocessingMetadata({'*', '"', "/", "*"},
#                                               word_boundaries=[0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
#
#     assert expected == actual
#     assert expected_metadata == actual_metadata

#
# #################################################
# ###   Only tests with single word go below
# #################################################
#
def test_1():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '4',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })

    tokens = [SplitContainer.from_single_token("Whi@le")]

    actual, actual_metadata = to_repr(prep_config, tokens, BpeData(merges_cache={'Whi@@le@': ['Whi@@le@']}))

    expected = ["Whi@le" + placeholders['compound_word_end']]

    expected_metadata = PreprocessingMetadata(word_boundaries=[0, 1], token_types=[SplitContainer])

    assert expected == actual
    assert expected_metadata == actual_metadata


def test_merges_no_cache():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '4',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })

    tokens = [SplitContainer.from_single_token("Whi@l@@e@")]

    actual, actual_metadata = to_repr(prep_config, tokens, BpeData(merges=MergeList().append(Merge(('W', 'h'), 10)),
                                                                    merges_cache={} ))

    expected = ["Wh", "i", '@', "l", '@', '@', "e", '@', pl["compound_word_end"]]

    expected_metadata = PreprocessingMetadata(word_boundaries=[0, 9], token_types=[SplitContainer])

    assert expected == actual
    assert expected_metadata == actual_metadata


def test_bpe_string_literal_performance():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '4',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })

    n= 10000
    tokens = [StringLiteral(['a' * n], n)]

    merge_list = MergeList()
    for i in range(1):
        merge_list.append(Merge(('a', 'a'), 10))
    start = time.perf_counter()
    to_repr(prep_config, tokens, BpeData(merges=merge_list, merges_cache={'Whi@@le@': ['Whi@@le@']}))
    assert (time.perf_counter() - start) < 1