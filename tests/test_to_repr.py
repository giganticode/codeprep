# SPDX-FileCopyrightText: 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import time

import pytest

from codeprep.bpepkg.bpe_encode import BpeData
from codeprep.bpepkg.merge import MergeList, Merge
from codeprep.preprocess.codestructure import PureSnippetStructure
from codeprep.preprocess.result import PreprocessingResult
from codeprep.preprocess.tokens import TokenSequence
from codeprep.tokentypes.containers import Identifier, OneLineComment, MultilineComment, StringLiteral
from codeprep.preprocess.metadata import PreppedTokenMetadata
from codeprep.tokentypes.noneng import NonEng
from codeprep.tokentypes.numeric import Number
from codeprep.preprocess.placeholders import placeholders
from codeprep.tokentypes.whitespace import Tab, NewLine, SpaceInString
from codeprep.tokentypes.word import Word, Underscore, NonCodeChar, Operator, StringLiteralQuote
from codeprep.prepconfig import PrepParam, PrepConfig
from codeprep.pipeline.to_repr import to_repr

pl = placeholders
cwe = placeholders['compound_word_end']

tokens = [
    Number('1.1'),
    Operator("*"),
    NonEng(Identifier([Word.from_("übersetzen")])),
    StringLiteralQuote('"'),
    StringLiteral([
        NonEng(
            Identifier([
                Word.from_("A"),
                Word.from_("Wirklicä")
            ])
        ),
        SpaceInString(1)
    ], 9),
    StringLiteralQuote('"'),
    NewLine(),
    MultilineComment([NonCodeChar('/'), NonCodeChar('*')]),
    MultilineComment([
        NonEng(
            Identifier([Word.from_('ц')]),
        ),
        NonEng(
            Identifier([
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
            Identifier([
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

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
        '1.1',
        "*",
        'übersetzen',
        '"', 'AWirklicä', '"',
        '/', '*', 'ц', 'blanco_english', '*', '/',
        '/', '/', "DIESELBE8", pl['olc_end']
    ], PreppedTokenMetadata(n_subtokens_per_token=[1] * 16,
                            token_types=[Number, Operator, Identifier,
                                         StringLiteralQuote, StringLiteral, StringLiteralQuote,
                                         MultilineComment, MultilineComment, MultilineComment,
                                         MultilineComment, MultilineComment, MultilineComment,
                                         OneLineComment, OneLineComment, OneLineComment, OneLineComment]),
        word_end_token_added=False, full_token_view=True),
        {'"', "*", "/"}, PureSnippetStructure.of([6, 6, 4]))

    assert result == expected_result


def test_to_repr_0_max_str_length_7():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '7',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
        '1.1',
        "*",
        'übersetzen',
        '"', '"',
        '/', '*', 'ц', 'blanco_english', '*', '/',
        '/', '/', "DIESELBE8", pl['olc_end']
    ], PreppedTokenMetadata(n_subtokens_per_token=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                            token_types=[Number, Operator, Identifier, StringLiteralQuote, StringLiteralQuote,
                                         MultilineComment, MultilineComment, MultilineComment,
                                         MultilineComment, MultilineComment, MultilineComment,
                                         OneLineComment, OneLineComment, OneLineComment, OneLineComment]),
    word_end_token_added=False, full_token_view=True),
                       {'"', "*", "/"}, PureSnippetStructure.of([5, 6, 4]))

    assert result == expected_result


def test_to_repr_0_max_str_length_B():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: 'B',
        PrepParam.SPLIT: '0',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
        '1.1',
        "*",
        'übersetzen',
        '"', "AWirklicä", '"',
        '/', '*', 'ц', 'blanco_english', '*', '/',
        '/', '/', "DIESELBE8", pl['olc_end']
    ], PreppedTokenMetadata(n_subtokens_per_token=[1] * 16,
                            token_types=[Number, Operator, Identifier,
                                         StringLiteralQuote, StringLiteral, StringLiteralQuote,
                                         MultilineComment, MultilineComment, MultilineComment,
                                         MultilineComment, MultilineComment, MultilineComment,
                                         OneLineComment, OneLineComment, OneLineComment, OneLineComment]), word_end_token_added=False, full_token_view=True),
        {'"', "*", "/"}, PureSnippetStructure.of([6, 6, 4]))

    assert result == expected_result


def test_to_repr_F():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
        '1.1',
        "*",
        'übersetzen',
        '"', 'AWirklicä\xa0', '"',
        '/', '*', 'ц', 'blanco_english', '*', '/',
        '/', '/', "DIESELBE8", pl['olc_end']
    ], PreppedTokenMetadata(n_subtokens_per_token=[1] * 16,
                            token_types=[Number, Operator, Identifier, StringLiteralQuote, StringLiteral, StringLiteralQuote,
                                         MultilineComment, MultilineComment, MultilineComment,
                                         MultilineComment, MultilineComment, MultilineComment,
                                         OneLineComment, OneLineComment, OneLineComment, OneLineComment]),
        word_end_token_added=False, full_token_view=True),
        {'"', "*", "/"}, PureSnippetStructure.of([6, 6, 4]))

    assert result == expected_result


def test_to_repr_F_max_str_length_7():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: '7',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
        '1.1',
        "*",
        'übersetzen',
        '"', '"',
        '/', '*', 'ц', 'blanco_english', '*', '/',
        '/', '/', "DIESELBE8", pl['olc_end']
    ], PreppedTokenMetadata(n_subtokens_per_token=[1] * 15,
                            token_types=[Number, Operator, Identifier, StringLiteralQuote, StringLiteralQuote,
                                         MultilineComment, MultilineComment, MultilineComment,
                                         MultilineComment, MultilineComment, MultilineComment,
                                         OneLineComment, OneLineComment, OneLineComment, OneLineComment]),
        word_end_token_added=False, full_token_view=True), {'"', "*", "/"}, PureSnippetStructure.of([5, 6, 4]))


    assert result == expected_result


def test_to_repr_F_max_str_length_B():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'u',
        PrepParam.COM: 'c',
        PrepParam.STR: 'B',
        PrepParam.SPLIT: 'F',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
        '1.1',
        "*",
        'übersetzen',
        '"', 'AWirklicä\xa0', '"',
        '/', '*', 'ц', 'blanco_english', '*', '/',
        '/', '/', "DIESELBE8", pl['olc_end']
    ], PreppedTokenMetadata(n_subtokens_per_token=[1] * 16,
                            token_types=[Number, Operator, Identifier, StringLiteralQuote, StringLiteral, StringLiteralQuote,
                                         MultilineComment, MultilineComment, MultilineComment,
                                         MultilineComment, MultilineComment, MultilineComment,
                                         OneLineComment, OneLineComment, OneLineComment, OneLineComment]),
        word_end_token_added=False, full_token_view=True),
    {'"', "*", "/"}, PureSnippetStructure.of([6, 6, 4]))

    assert result == expected_result

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

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
        '1.1',
        "*",
        pl['non_eng'],
        '"',
        pl['non_eng'], '"',
        '/', '*', pl['non_eng'], pl['non_eng'], '*', '/',
        '/', '/', pl['non_eng'],
        pl['olc_end']
    ], PreppedTokenMetadata(n_subtokens_per_token=[1] * 16,
                            token_types=[Number, Operator, NonEng,
                                                           StringLiteralQuote, StringLiteral, StringLiteralQuote,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           OneLineComment, OneLineComment, OneLineComment, OneLineComment]),
    word_end_token_added=False, full_token_view=True),
        {'*', '"', "/", "*"}, PureSnippetStructure.of([6, 6, 4]))

    assert result == expected_result

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

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
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
    ], PreppedTokenMetadata(n_subtokens_per_token=[5] + [1] * 15,
                            token_types=[Number, Operator, NonEng,
                                                           StringLiteralQuote, StringLiteral, StringLiteralQuote,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           MultilineComment, MultilineComment, MultilineComment,
                                                           OneLineComment, OneLineComment, OneLineComment, OneLineComment]),
        word_end_token_added=False, full_token_view=True),
        {'*', '"', "/", "*"}, PureSnippetStructure.of([10, 6, 4]))

    assert result == expected_result

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
        NonEng(Identifier([Word.from_("dinero")])),
        StringLiteral([
            NonCodeChar('"'),
            NonEng(Identifier([Word.from_("ich")])),
            SpaceInString(),
            NonEng(Identifier([Word.from_("weiss")])),
            SpaceInString(),
            NonEng(Identifier([Word.from_("nicht")])),
            SpaceInString(),
            NonEng(Identifier([Word.from_("was")])),
            SpaceInString(),
            NonEng(Identifier([Word.from_("soll")])),
            SpaceInString(),
            NonEng(Identifier([Word.from_("es")])),
            SpaceInString(),
            NonEng(Identifier([Word.from_("bedeuten")])),
            SpaceInString(),
            NonEng(Identifier([Word.from_("dass")])),
            SpaceInString(),
            NonEng(Identifier([Word.from_("ich")])),
            SpaceInString(),
            NonEng(Identifier([Word.from_("so")])),
            SpaceInString(),
            NonEng(Identifier([Word.from_("traurig")])),
            SpaceInString(),
            NonEng(Identifier([Word.from_("bin")])),
            NonCodeChar('"'),
        ], 62),
        NewLine(),
        MultilineComment([NonCodeChar('/'), NonCodeChar('*')]),
        MultilineComment([
            NonEng(Identifier([Word.from_('ц')])),
            NonEng(
                Identifier([
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
                Identifier([
                    Word.from_("DIESELBE"),
                    Word.from_("8")
                ])
            )
        ])
    ]

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
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
    ], PreppedTokenMetadata(n_subtokens_per_token=[5] + [1] * 26,
                            token_types=[Number, Operator, NonEng]
                                                          + [StringLiteral] * 14
                                                          + [MultilineComment] * 6
                                                          + [OneLineComment] * 4), word_end_token_added=False, full_token_view=True),
        {'*', '"', "/", "*"}, PureSnippetStructure.of([21, 6, 4]))

    assert result == expected_result

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

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
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
    ], PreppedTokenMetadata(n_subtokens_per_token=[5, 1, 1, 1, 6, 1, 1, 1, 1,
                                                   5, 1, 1, 1, 1, 5, 1],
                            token_types=[Number, Operator, Identifier]
                                                          + [StringLiteralQuote, StringLiteral, StringLiteralQuote]
                                                          + [MultilineComment] * 6
                                                          + [OneLineComment] * 4), word_end_token_added=False, full_token_view=True),
    {'"', "/", '*'}, PureSnippetStructure.of([15, 10, 8]))

    assert result == expected_result

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

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
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
    ], PreppedTokenMetadata(
        n_subtokens_per_token=[5] + [1] * 18,
        token_types=[Number, Operator, NonEng]
                                                          + [StringLiteralQuote, StringLiteral, StringLiteralQuote] + [NewLine]
                                                          + [MultilineComment] * 6 + [NewLine, Tab]
                                                          + [OneLineComment] * 4), word_end_token_added=False, full_token_view=True),
        {'*', "/", '\n', '\t', '"'}, PureSnippetStructure.of([11, 7, 5]))

    assert result == expected_result

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

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
        pl['word_start'],
        '1',
        '.',
        '1',
        pl['word_end'],
        "*",
        pl['non_eng'],
        '"',
        pl["string_literal"],
        '"',
        pl["comment"],
        pl["comment"],
        pl["comment"],
        pl["comment"]
    ], PreppedTokenMetadata(n_subtokens_per_token=[5] + [1] * 9,
                            token_types=[Number, Operator, NonEng, StringLiteralQuote, StringLiteral, StringLiteralQuote,
                                                           MultilineComment, MultilineComment, MultilineComment, OneLineComment]), word_end_token_added=False, full_token_view=True),

        {'*', '"'}, PureSnippetStructure.of([10, 3, 1]))

    assert result == expected_result

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

    result = to_repr(prep_config, tokens)

    expected_result = PreprocessingResult(TokenSequence.create([
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
    ], PreppedTokenMetadata(n_subtokens_per_token=[5] + [1] * 15,
                            token_types=[Number, Operator, NonEng]
                                                          + [StringLiteralQuote, StringLiteral, StringLiteralQuote]
                                                          + [MultilineComment] * 6
                                                          + [OneLineComment] * 4), word_end_token_added=False, full_token_view=True),
        {'*', '"', "/"}, PureSnippetStructure.of([10, 6, 4]))

    assert result == expected_result


def test_to_repr_no_no_sep_with_bpe_no_merges():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '4',
        PrepParam.TABS_NEWLINES: '0',
        PrepParam.CASE: 'u'
    })

    result = to_repr(prep_config, tokens, BpeData(merges_cache={}, merges=MergeList()))

    expected = [
        '1',
        '.',
        '1',
        cwe,
        "*" + cwe,
        '÷', 'b', 'e', 'r', 's', 'e', 't', 'z', 'e', 'n', '</t>',
        '"' + cwe, 'A', 'W', 'i', 'r', 'k', 'l', 'i', 'c', '\xf7', '\xa0', cwe, '"' + cwe,
        '/' + cwe, '*' + cwe, '\xf7', cwe, 'b', 'l', 'a', 'n', 'c', 'o', '_', 'e', 'n', 'g', 'l', 'i', 's', 'h', cwe, '*' + cwe, '/' + cwe,
        '/' + cwe, '/' + cwe, 'D', 'I', 'E', 'S', 'E', 'L', 'B', 'E', '8', cwe,
        pl['olc_end'] + cwe
    ]

    assert result.prepped_tokens._tokens == expected


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
#     expected_metadata = PreppedTokenMetadata({'*', '"', "/", "*"},
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

    tokens = [Identifier.from_single_token("Whi@le")]

    result = to_repr(prep_config, tokens, BpeData(merges_cache={'Whi@@le@': ['Whi@@le@']}))

    expected_result = PreprocessingResult(TokenSequence.create(["Whi@le" + placeholders['compound_word_end']],
                                                               PreppedTokenMetadata(n_subtokens_per_token=[1],
                                                                                token_types=[Identifier]),
                                                               word_end_token_added=True),
                                          set(), PureSnippetStructure.of([1]))

    assert result == expected_result


def test_merges_no_cache():
    prep_config = PrepConfig({
        PrepParam.EN_ONLY: 'U',
        PrepParam.COM: 'c',
        PrepParam.STR: '1',
        PrepParam.SPLIT: '4',
        PrepParam.TABS_NEWLINES: 's',
        PrepParam.CASE: 'u'
    })

    tokens = [Identifier.from_single_token("Whi@l@@e@")]

    result = to_repr(prep_config, tokens, BpeData(merges=MergeList().append(Merge(('W', 'h'), 10)),
                                                                    merges_cache={} ))

    expected_result = PreprocessingResult(
        TokenSequence.create(["Wh", "i", '@', "l", '@', '@', "e", '@', pl["compound_word_end"]],
                             PreppedTokenMetadata(n_subtokens_per_token=[9], token_types=[Identifier]), word_end_token_added=True),
        set(), PureSnippetStructure.of([9]))

    assert result == expected_result


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