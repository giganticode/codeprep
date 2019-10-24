import bisect
import logging
from dataprep.util import to_literal_str
from typing import Set, Optional, List, Tuple, Any

logger = logging.getLogger(__name__)


class PreprocessingMetadata(object):
    def __init__(self,
                 nonprocessable_tokens: Optional[Set[str]] = None,
                 word_boundaries: Optional[List[int]] = None,
                 comments: List[Tuple[int, int]] = None):
        self.nonprocessable_tokens = nonprocessable_tokens or set()
        self.word_boundaries = word_boundaries or [0]
        self.comments = comments or []

    def set_all_tokens_comment(self) -> None:
        self.comments = [(self.word_boundaries[0], self.word_boundaries[-1])]

    def update(self, preprocessing_metadata: 'PreprocessingMetadata') -> 'PreprocessingMetadata':
        """
        >>> PreprocessingMetadata().update(PreprocessingMetadata())
        (set(), [0], [])

        >>> PreprocessingMetadata({'<comment>'}, [0, 2], []).update(PreprocessingMetadata({'<comment>'}, [0, 3], [(1, 2)]))
        ({'<comment>'}, [0, 2, 5], [(3, 4)])

        >>> PreprocessingMetadata(set(), [0, 2], [(0, 2)]).update(PreprocessingMetadata(set(), [0, 3], [(0, 3)]))
        (set(), [0, 2, 5], [(0, 5)])
        """
        self.nonprocessable_tokens.update(preprocessing_metadata.nonprocessable_tokens)

        n_subtokens = self.word_boundaries.pop()
        for boundary in preprocessing_metadata.word_boundaries:
            self.word_boundaries.append(n_subtokens + boundary)

        self._update_comments(preprocessing_metadata.comments, n_subtokens)
        return self

    def _update_comments(self, comments: List[Tuple[int, int]], n_subtokens: int) -> None:
        if comments:
            adjusted_comments = [(c[0] + n_subtokens, c[1] + n_subtokens) for c in comments]
            if self.comments and adjusted_comments[0][0] == n_subtokens and self.comments[-1][1] == n_subtokens:
                self.comments[-1] = (self.comments[-1][0], adjusted_comments[0][1])
            else:
                self.comments.append(adjusted_comments[0])
            self.comments += adjusted_comments[1:]

    def is_comment_at_index(self, current_index: int):
        """
        >>> PreprocessingMetadata(set(), [0, 1000], []).is_comment_at_index(5)
        False

        >>> PreprocessingMetadata(set(), [0, 1000], [(0, 5), (6, 10)]).is_comment_at_index(5)
        False

        >>> PreprocessingMetadata(set(), [0, 1000], [(5, 10)]).is_comment_at_index(5)
        True

        >>> PreprocessingMetadata(set(), [0, 1000], [(0, 6)]).is_comment_at_index(5)
        True

        >>> PreprocessingMetadata(set(), [0, 1000], [(0, 1), (2, 3), (500, 600)]).is_comment_at_index(5)
        False
        """
        ind = bisect.bisect_right(list(map(lambda a: a[0], self.comments)), current_index) - 1
        return ind != -1 and self.comments[ind][0] <= current_index < self.comments[ind][1]

    def __repr__(self):
        return str((self.nonprocessable_tokens, self.word_boundaries, self.comments))

    def __eq__(self, other):
        return self.__class__ == other.__class__ \
               and self.nonprocessable_tokens == other.nonprocessable_tokens \
               and self.word_boundaries == other.word_boundaries \
               and self.comments == other.comments


def save_metadata(metadata: PreprocessingMetadata, save_to: bytes):
    with open(save_to, 'w') as f:
        for token in metadata.nonprocessable_tokens:
            f.write(f'{to_literal_str(token)}\n')


def check_metadata_validity(subwords: List[Any], metadata: PreprocessingMetadata) -> None:
    word_boundaries = metadata.word_boundaries
    if len(word_boundaries) == 0:
        raise ValueError("Word boundaries list should contain at least 0!")
    if len(subwords) != word_boundaries[-1]:
        raise ValueError(f"Word boundaries list should contain the indices of the last word.\n"
                         f"However, the subword entropies list has {len(subwords)} elements, and "
                         f"value {len(subwords)} is not found in word boundaries list: {word_boundaries}")
    if word_boundaries[0] != 0:
        raise ValueError('Word boundaries list must start with 0!')
