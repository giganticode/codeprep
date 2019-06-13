from typing import List, Tuple

from dataprep.model.core import ParsedToken, ParsedSubtoken
from dataprep.model.metadata import PreprocessingMetadata
from dataprep.model.placeholders import placeholders
from dataprep.model.word import Word
from dataprep.preprocess.core import ReprConfig, torepr


class NonEng(ParsedSubtoken):
    def __init__(self, processable_token):
        if not isinstance(processable_token, Word):
            raise ValueError(f"NonEngFullWord excepts FullWord but {type(processable_token)} is passed")

        self.processable_token = processable_token

    def non_preprocessed_repr(self, repr_config) -> Tuple[List[str], PreprocessingMetadata]:
        return torepr(self.processable_token, repr_config)

    def preprocessed_repr(self, repr_config: ReprConfig) -> Tuple[List[str], PreprocessingMetadata]:
        # TODO refactor -> move this logic to parser
        if not repr_config.dict_based_non_eng:
            s, metadata = self.processable_token.non_preprocessed_repr(repr_config)
            try:
                s.encode('ascii')
                return torepr(self.processable_token, repr_config)
            except UnicodeEncodeError:
                repr, metadata = torepr(self.processable_token, repr_config)
                if repr[0] in [placeholders['capitals'], placeholders['capital']]:
                    prep_tokens = [repr[0], placeholders['non_eng']]
                else:
                    prep_tokens = [placeholders['non_eng']]
                return self.with_empty_metadata(prep_tokens)
        repr, metadata = torepr(self.processable_token, repr_config)
        if repr[0] in [placeholders['capitals'], placeholders['capital']]:
            prep_tokens = [repr[0], placeholders['non_eng']]
        else:
            prep_tokens = [placeholders['non_eng']]
        return self.with_empty_metadata(prep_tokens)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.processable_token.__repr__()})'

    def __str__(self):
        return str(self.processable_token)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.processable_token == other.processable_token


class NonEngContent(ParsedToken):
    pass
