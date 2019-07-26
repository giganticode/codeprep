import unittest

from dataprep.bpepkg.bpe_encode import BpeData
from dataprep.parse.core import convert_text
from dataprep.parse.model.containers import SplitContainer
from dataprep.parse.model.numeric import Number
from dataprep.parse.model.placeholders import placeholders
from dataprep.parse.model.word import Underscore, Word
from dataprep.prepconfig import PrepConfig
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
        [Number("0.345e+4")],
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


class SubwordSeparation(unittest.TestCase):
    def test(self):
        for input, output_tuple in test_cases.items():
            parsed = [p for p in convert_text(input, "java")][:-1]

            self.assertEqual(output_tuple[0], parsed)

            repred, metadata = to_repr(PrepConfig.from_encoded_string('Uc140l'), parsed, BpeData(merges_cache=bpe_merges_cache))

            self.assertEqual(output_tuple[1], repred)


if __name__ == '__main__':
    unittest.main()
