import logging
from typing import Set, Optional

logger = logging.getLogger(__name__)


class PreprocessingMetadata():
    def __init__(self, nonprocessable_tokens: Optional[Set[str]] = None):
        self.nonprocessable_tokens = nonprocessable_tokens or set()

    def update(self, preprocessing_metadata: 'PreprocessingMetadata'):
        self.nonprocessable_tokens.update(preprocessing_metadata.nonprocessable_tokens)

    def __repr__(self):
        return str(self.nonprocessable_tokens)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.nonprocessable_tokens == other.nonprocessable_tokens


def save_metadata(metadata: PreprocessingMetadata, save_to: bytes):
    with open(save_to, 'w') as f:
        for token in metadata.nonprocessable_tokens:
            f.write(f'{token.encode()}\n')
