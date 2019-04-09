from typing import List

from dataprep.model.placeholders import placeholders
from dataprep.model.word import Word
from dataprep.preprocessors.repr import torepr, ReprConfig


class NonEng(object):
    def __init__(self, processable_token):
        if not isinstance(processable_token, Word):
            raise ValueError(f"NonEngFullWord excepts FullWord but {type(processable_token)} is passed")

        self.processable_token = processable_token

    def non_preprocessed_repr(self, repr_config):
        return torepr(self.processable_token, repr_config)

    def preprocessed_repr(self, repr_config: ReprConfig) -> List[str]:
        # TODO refactor -> move this logic to parser
        if not repr_config.dict_based_non_eng:
            s = self.processable_token.non_preprocessed_repr(repr_config)
            try:
                s.encode('ascii')
                return torepr(self.processable_token, repr_config)
            except UnicodeEncodeError:
                repr = torepr(self.processable_token, repr_config)
                if repr[0] in [placeholders['capitals'], placeholders['capital']]:
                    return [repr[0], placeholders['non_eng']]
                else:
                    return [placeholders['non_eng']]
        repr = torepr(self.processable_token, repr_config)
        if repr[0] in [placeholders['capitals'], placeholders['capital']]:
            return [repr[0], placeholders['non_eng']]
        else:
            return [placeholders['non_eng']]

    def __repr__(self):
        return f'{self.__class__.__name__}({self.processable_token.__repr__()})'

    def __str__(self):
        return str(self.processable_token)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.processable_token == other.processable_token


class NonEngContent(object):
    pass
