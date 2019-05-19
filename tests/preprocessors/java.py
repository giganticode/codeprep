import unittest

from dataprep.preprocessors.java import process_comments_and_str_literals
from dataprep.model.chars import OneLineCommentStart, NewLine, Quote, MultilineCommentStart, MultilineCommentEnd


# TODO write explanations with normal strings
from dataprep.model.containers import SplitContainer, StringLiteral, OneLineComment, MultilineComment
from dataprep.model.word import Word, Underscore


class JavaTest(unittest.TestCase):
    def test_process_comments_and_str_literals(self):
        '''
        Positive scenario

        <start>"//test_MyClass"
        //*/
        "/*!"
        /*
        /*
        <end>


        '''
        tokens = [Quote(),
                  OneLineCommentStart(),
                  SplitContainer([Word.from_("test"),
                                  Underscore(),
                                  Word.from_("my"),
                                  Word.from_("Class")]),
                  Quote(),
                  NewLine(),
                  OneLineCommentStart(),
                  MultilineCommentEnd(),
                  NewLine(),
                  Quote(),
                  MultilineCommentStart(),
                  SplitContainer.from_single_token("!"),
                  Quote(),
                  NewLine(),
                  MultilineCommentStart(),
                  NewLine(),
                  MultilineCommentEnd(),
                  NewLine(),
                  ]

        actual = process_comments_and_str_literals(tokens)

        expected = [StringLiteral([Quote(), OneLineCommentStart(), SplitContainer([
            Word.from_("test"),
            Underscore(),
            Word.from_("my"),
            Word.from_("Class")],
        ), Quote()]),
                    NewLine(),
                    OneLineComment([OneLineCommentStart(), MultilineCommentEnd()]),
                    NewLine(),
                    StringLiteral([Quote(), MultilineCommentStart(),
                                   SplitContainer.from_single_token("!"), Quote()]),
                    NewLine(),
                    MultilineComment([MultilineCommentStart(), NewLine(), MultilineCommentEnd()]),
                    NewLine()
                    ]

        self.assertEqual(expected, actual)

    def test_process_comments_and_str_literals_no_multiline_comment_start(self):
        tokens = [MultilineCommentEnd(), Word.from_("a")]

        actual = process_comments_and_str_literals(tokens)

        expected = [MultilineCommentEnd(), Word.from_("a")]

        self.assertEqual(expected, actual)

    def test_process_comments_and_str_literals_newline_after_open_quote(self):
        tokens = [Quote(), NewLine()]

        actual = process_comments_and_str_literals(tokens)

        expected = [Quote(), NewLine()]

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
