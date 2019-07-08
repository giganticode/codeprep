import logging
from typing import List, Optional, Tuple

from dataprep.parse.model.placeholders import placeholders

logger = logging.getLogger(__name__)

capitals = [placeholders['capital'], placeholders['capitals']]

ignorable_tokens = [
    placeholders['ect']
]


class FullWordIterator(object):
    def __init__(self, targets: Optional[List[str]] = None, exit_on_error=False):
        if targets is None:
            self.exhausted = True
            self.targets = []
        else:
            self.exhausted = False
            self.targets = targets
        self.exit_on_error = exit_on_error
        self.current_index = 0

    def add_data(self, targets: List[str]) -> None:
        if not self.exhausted:
            raise ValueError('Adding data is possible only when iterator is exhausted')

        self.targets.extend(targets)
        self.exhausted = False

    def get_chunks_left(self) -> int:
        if not self.exhausted:
            raise ValueError('Getting left chunks is possible only when iterator is exhausted')

        return len(self.targets)

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[List[str], Tuple[int, int]]:
        word_in_progress = False
        after_full_word_capital = False
        index_from = self.current_index
        index_to = None
        while self.current_index < len(self.targets):
            current_target_word = self.targets[self.current_index]

            if after_full_word_capital:
                after_full_word_capital = False
                index_to = self.current_index + 1
            elif not word_in_progress:
                if current_target_word in ignorable_tokens:
                    index_from += 1
                    self.current_index += 1
                    continue
                elif current_target_word == placeholders['word_start']:
                    word_in_progress = True
                elif current_target_word in capitals:
                    after_full_word_capital = True
                elif current_target_word == placeholders['word_end']:
                    message = f"Word end separator without word start at {self.targets}, position {self.current_index}"
                    if self.exit_on_error:
                        raise AssertionError(message)
                    else:
                        logger.warning(message)
                        index_from += 1
                        continue
                else:
                    index_to = self.current_index + 1
            else:
                if current_target_word == placeholders['word_end']:
                    index_to = self.current_index + 1
                    word_in_progress = False
            self.current_index += 1
            if not word_in_progress and not after_full_word_capital:
                break
        if index_to:
            return self.targets[index_from: index_to], (index_from, index_to)
        else:
            self.targets = self.targets[index_from:]
            self.current_index = 0
            self.exhausted = True
            raise StopIteration()


class SubwordsIterator(object):
    def __init__(self, targets: Optional[List[str]] = None):
        if targets is None:
            self.exhausted = True
            self.targets = []
        else:
            self.exhausted = False
            self.targets = targets
        self.current_index = 0

    def add_data(self, targets: List[str]) -> None:
        if not self.exhausted:
            raise ValueError('Adding data is possible only when iterator is exhausted')

        self.targets = targets
        self.exhausted = False

    def get_chunks_left(self) -> int:
        if not self.exhausted:
            raise ValueError('Getting left chunks is possible only when iterator is exhausted')

        return 0

    def __iter__(self):
        return self

    def __next__(self) -> Tuple[List[str], Tuple[int, int]]:
        if self.current_index >= len(self.targets):
            self.current_index = 0
            self.exhausted = True
            raise StopIteration()

        target = self.targets[self.current_index]
        ind = self.current_index
        self.current_index += 1
        return [target], (ind, ind + 1)
