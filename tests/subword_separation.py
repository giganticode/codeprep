import unittest

from dataprep.preprocessors.core import from_string, _apply_preprocessors
from dataprep.preprocessors.preprocessor_list import pp_params
from dataprep.model.containers import SplitContainer, StringLiteral
from dataprep.model.numeric import Number, DecimalPoint, E
from dataprep.model.placeholders import placeholders
from dataprep.model.word import Word, Underscore
from dataprep.prepconfig import PrepConfig
from dataprep.split.ngram import NgramSplitConfig, NgramSplittingType
from dataprep.to_repr import to_repr

test_cases = {
    "create": (
        [SplitContainer.from_single_token("create")],
        ["create"],
    ),
    "Vector": (
        [SplitContainer.from_single_token("Vector")],
        [placeholders["capital"], "vector"],
    ),
    "players": (
        [SplitContainer.from_single_token("players")],
        [placeholders["word_start"], 'play', 'er', 's', placeholders["word_end"]]
    ),
    "0.345e+4": (
        [Number(["0", DecimalPoint(), "3", "4", "5", E(), "+", "4"])],
        [placeholders["word_start"], "0.", "3", "4", "5", "e+", "4", placeholders["word_end"]]
    ),
    "bestPlayers": (
        [SplitContainer([Word.from_("best"), Word.from_("Players")])],
        [placeholders["word_start"], "best", placeholders["capital"], 'play', "er", "s", placeholders["word_end"]]
    ),
    "test_BestPlayers": (
        [SplitContainer([Word.from_("test"), Underscore(), Word.from_("Best"), Word.from_("Players")])],
        [placeholders["word_start"], "test", '_', placeholders["capital"],
         "best", placeholders["capital"], 'play', "er", "s", placeholders["word_end"]]
    ),
    "test_BestPlayers_modified": (
        [SplitContainer(
            [Word.from_("test"), Underscore(), Word.from_("Best"), Word.from_("Players"), Underscore(),
             Word.from_("modified")]
        )],
        [placeholders["word_start"], "test", '_', placeholders["capital"],
         "best", placeholders["capital"], 'play', "er", "s", '_', "mod",
         "if", "ied",
         placeholders["word_end"]]
    ),
    "N_PLAYERS_NUM": (
        [SplitContainer([Word.from_("N"), Underscore(), Word.from_("PLAYERS"), Underscore(), Word.from_("NUM")])],
        [placeholders["word_start"], placeholders["capitals"], "n", '_',
         placeholders["capitals"], "play", "er", "s", '_', placeholders["capitals"],
         "num", placeholders["word_end"]]
    ),
    "_players": (
        [SplitContainer([Underscore(), (Word.from_("players"))])],
        [placeholders['word_start'], '_', "play", "er", "s", placeholders['word_end']]
    ),
}

bpe_merges_cache = {
    "players": ["play", "er", "s"],
    "0.345e+4": ["0.", "3", "4", "5", "e+", "4"],
    "modified": ["mod", "if", "ied"],

    "create": ["create"],
    "vector": ["vector"],
    "best": ["best"],
    "test": ["test"],
    "num": ["num"],
    "user": ["user"],
    "get": ["get"],
    "nick": ["ni", "ck"],
    "logger": ["logger"],
    "info": ["info"]
}

ngram_split_config = NgramSplitConfig(NgramSplittingType.BPE, merges_cache=bpe_merges_cache, merges={})


class SubwordSeparation(unittest.TestCase):
    def test(self):
        for input, output_tuple in test_cases.items():
            parsed = _apply_preprocessors(from_string(input), pp_params["preprocessors"])

            self.assertEqual(output_tuple[0], parsed)

            repred = to_repr(PrepConfig.from_encoded_string('30411'), parsed, ngram_split_config)

            self.assertEqual(output_tuple[1], repred)


if __name__ == '__main__':
    unittest.main()
