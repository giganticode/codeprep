from typing import List, Tuple, Optional

from dataprep.parse.model.containers import SplitContainer
from dataprep.parse.model.core import ParsedToken, with_empty_metadata
from dataprep.parse.model.metadata import PreprocessingMetadata
from dataprep.parse.model.placeholders import placeholders
from dataprep.preprocess.core import ReprConfig, torepr


class NonEng(ParsedToken):
    def __init__(self, processable_token: SplitContainer):
        if not isinstance(processable_token, SplitContainer):
            raise ValueError(f"Only SplitContainer can be wrapped in {self.__class__}. Type passed: {type(processable_token)}")

        self.processable_token = processable_token

    def non_preprocessed_repr(self, repr_config: Optional[ReprConfig] = None) -> Tuple[List[str], PreprocessingMetadata]:
        return torepr(self.processable_token, repr_config)

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        return with_empty_metadata([placeholders['non_eng']])

    def __repr__(self):
        return f'{self.__class__.__name__}({self.processable_token.__repr__()})'

    def __str__(self):
        return str(self.processable_token)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.processable_token == other.processable_token


class NonEngContent(ParsedToken):
    pass
