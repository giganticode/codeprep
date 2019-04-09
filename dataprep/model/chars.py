from typing import List

from dataprep.preprocessors.repr import ReprConfig


class SpecialChar(object):
    def __eq__(self, other):
        return other.__class__ == self.__class__

    def __repr__(self):
        return f'<{self.__class__.__name__}>'

    def __str__(self):
        return self.non_preprocessed_repr(ReprConfig.empty())


class NewLine(SpecialChar):
    def non_preprocessed_repr(self, repr_config):
        return "\n"

    def preprocessed_repr(self, repr_config) -> List[str]:
        return []


class Tab(SpecialChar):
    def non_preprocessed_repr(self, repr_config):
        return "\t"

    def preprocessed_repr(self, repr_config) -> List[str]:
        return []


class Backslash(SpecialChar):
    def non_preprocessed_repr(self, repr_config):
        return "\\"


class Quote(SpecialChar):
    def non_preprocessed_repr(self, repr_config):
        return "\""


class MultilineCommentStart(SpecialChar):
    def non_preprocessed_repr(self, repr_config):
        return "/*"


class MultilineCommentEnd(SpecialChar):
    def non_preprocessed_repr(self, repr_config):
        return "*/"


class OneLineCommentStart(SpecialChar):
    def non_preprocessed_repr(self, repr_config):
        return "//"
