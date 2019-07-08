import logging
from typing import Set, Optional, List

logger = logging.getLogger(__name__)


class PreprocessingMetadata():
    def __init__(self, nonprocessable_tokens: Optional[Set[str]] = None, word_boundaries: Optional[List[int]] = None):
        self.nonprocessable_tokens = nonprocessable_tokens or set()
        self.word_boundaries = word_boundaries or [0]

    def update(self, preprocessing_metadata: 'PreprocessingMetadata'):
        self.nonprocessable_tokens.update(preprocessing_metadata.nonprocessable_tokens)

        n_subtokens = self.word_boundaries.pop()
        for boundary in preprocessing_metadata.word_boundaries:
            self.word_boundaries.append(n_subtokens + boundary)

    def __repr__(self):
        return str((self.nonprocessable_tokens, self.word_boundaries))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.nonprocessable_tokens == other.nonprocessable_tokens \
               and self.word_boundaries == other.word_boundaries


def save_metadata(metadata: PreprocessingMetadata, save_to: bytes):
    with open(save_to, 'w') as f:
        for token in metadata.nonprocessable_tokens:
            f.write(f'{repr(token)[1:-1]}\n')
