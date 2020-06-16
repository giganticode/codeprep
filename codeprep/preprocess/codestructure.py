# SPDX-FileCopyrightText: 2020 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import bisect
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional

from codeprep.util.misc import cum_sum


@dataclass
class PureSnippetStructure:
    subtokens_in_each_line: List[int]

    @staticmethod
    def empty() -> 'PureSnippetStructure':
        return PureSnippetStructure([0])

    @staticmethod
    def empty_line() -> 'PureSnippetStructure':
        return PureSnippetStructure([0, 0])

    def __len__(self) -> int:
        return sum(self.subtokens_in_each_line)

    def tie_to_working_dir(self, path: Path, first_line: int) -> 'SnippetStructure':
        return SnippetStructure(path, self.subtokens_in_each_line, first_line)

    def merge(self, other: 'PureSnippetStructure') -> 'AbstractCodeSnippetStructured':
        lines_combines = self.subtokens_in_each_line[:-1] + \
                         [self.subtokens_in_each_line[-1] + other.subtokens_in_each_line[0]] + \
                         other.subtokens_in_each_line[1:]
        return PureSnippetStructure(lines_combines)

    def split(self, second_part_start_index: int) -> Tuple['PureSnippetStructure', 'PureSnippetStructure']:
        cumulative_lengths = cum_sum(self.subtokens_in_each_line)
        line_to_be_split = bisect.bisect_right(cumulative_lengths, second_part_start_index, 0, len(cumulative_lengths))
        total_lengths_of_previous_lines = cumulative_lengths[line_to_be_split-1] if line_to_be_split > 0 else 0
        position_to_split_in_line = second_part_start_index - total_lengths_of_previous_lines

        lines_in_first = self.subtokens_in_each_line[:line_to_be_split]
        if line_to_be_split < len(self.subtokens_in_each_line):
            lines_in_first.append(position_to_split_in_line)
            first_line_in_second = [self.subtokens_in_each_line[line_to_be_split] - position_to_split_in_line]
        else:
            first_line_in_second = [0]
        lines_in_second = first_line_in_second + self.subtokens_in_each_line[line_to_be_split+1:]
        return PureSnippetStructure(lines_in_first), PureSnippetStructure(lines_in_second)


@dataclass
class SnippetStructure:
    """
    >>> snippet_a = SnippetStructure(Path(''), [3], 2)
    >>> snippet_a.split(4)
    (.: [3], first-line: 2, .: [0], first-line: 2)
    >>> snippet_a.split(0)
    (.: [0], first-line: 2, .: [3], first-line: 2)
    >>> snippet_a.split(2)
    (.: [2], first-line: 2, .: [1], first-line: 2)
    >>> snippet_a.split(3)
    (.: [3], first-line: 2, .: [0], first-line: 2)

    >>> snippet_b = SnippetStructure(Path(''), [3, 0, 0, 4], 2)
    >>> snippet_b.split(3)
    (.: [3, 0, 0, 0], first-line: 2, .: [4], first-line: 5)
    >>> snippet_b.split(4)
    (.: [3, 0, 0, 1], first-line: 2, .: [3], first-line: 5)
    >>> snippet_b.split(7)
    (.: [3, 0, 0, 4], first-line: 2, .: [0], first-line: 5)

    """
    path: Path
    subtokens_in_each_line: List[int]
    first_line: int

    def untie_from_file(self) -> PureSnippetStructure:
        return PureSnippetStructure(self.subtokens_in_each_line)

    def merge(self, other: 'SnippetStructure') -> 'SnippetStructure':
        if self.path is not None and other.path is not None and self.path != other.path:
            raise ValueError("Cannot merge two different files.")
        path = self.path if self.path is not None else other.path

        if self.first_line is not None and other.first_line is not None and \
                self.first_line + len(self.subtokens_in_each_line) - 1 != other.first_line:
            raise ValueError("Prepped files are not adjacent.")

        merged = self.untie_from_file().merge(other.untie_from_file())
        return merged.tie_to_working_dir(path, self.first_line)

    def split(self, second_part_start_index: int) -> Tuple['SnippetStructure', 'SnippetStructure']:
        snippet1, snippet2 = self.untie_from_file().split(second_part_start_index)

        return snippet1.tie_to_working_dir(self.path, self.first_line), \
               snippet2.tie_to_working_dir(self.path, self.first_line + len(snippet1.subtokens_in_each_line) -1)

    def __len__(self) -> int:
        return len(self.untie_from_file())

    def __repr__(self):
        return f'{self.path}: {self.subtokens_in_each_line}, first-line: {self.first_line}'


@dataclass
class CodeBaseStructure:
    """
    >>> snippet = SnippetStructure(Path(''), [3, 4], 2)
    >>> snippet_a, snippet_b = snippet.split(5)
    >>> prepped_code = CodeBaseStructure([snippet_a, snippet_b])
    >>> prepped_code.split(2)
    (CodeBaseStructure(snippets=[.: [2], first-line: 2]), CodeBaseStructure(snippets=[.: [1, 2], first-line: 2, .: [2], first-line: 3]))
    >>> prepped_code.split(7)
    (CodeBaseStructure(snippets=[.: [3, 2], first-line: 2, .: [2], first-line: 3]), CodeBaseStructure(snippets=[]))
    >>> prepped_code.split(99)
    (CodeBaseStructure(snippets=[.: [3, 2], first-line: 2, .: [2], first-line: 3]), CodeBaseStructure(snippets=[]))

    """
    snippets: List[SnippetStructure] = field(default_factory=list)

    def add_snippet(self, prepped_snippet: SnippetStructure) -> 'CodeBaseStructure':
        if not self.snippets or self.snippets[-1].path != prepped_snippet.path:
            self.snippets.append(prepped_snippet)
        else:
            self.snippets[-1] = self.snippets[-1].merge(prepped_snippet)
        return self

    def merge(self, code_base_structure: 'CodeBaseStructure') -> 'CodeBaseStructure':
        for snippet in code_base_structure.snippets:
            self.add_snippet(snippet)
        return self

    def _get_cumularive_snippet_lengths(self) -> List[int]:
        return cum_sum(map(lambda x: len(x), self.snippets))

    def split(self, second_part_start_index: int) -> Tuple['CodeBaseStructure', 'CodeBaseStructure']:
        cumulative_lengths = self._get_cumularive_snippet_lengths()
        snippet_to_be_split = bisect.bisect_right(cumulative_lengths, second_part_start_index, 0, len(cumulative_lengths))
        total_lengths_of_previous_snippets = cumulative_lengths[snippet_to_be_split-1] if snippet_to_be_split > 0 else 0
        position_to_split_in_snippet = second_part_start_index - total_lengths_of_previous_snippets
        if snippet_to_be_split < len(cumulative_lengths):
            first, second = self.snippets[snippet_to_be_split].split(position_to_split_in_snippet)
            snippets_in_first = self.snippets[:snippet_to_be_split]
            if len(first) > 0:
                snippets_in_first.append(first)
            snippets_in_second = [second] + self.snippets[snippet_to_be_split+1:]
            return CodeBaseStructure(snippets_in_first), CodeBaseStructure(snippets_in_second)
        else:
            return CodeBaseStructure(self.snippets), CodeBaseStructure()

    def pop(self) -> Optional[SnippetStructure]:
        if len(self.snippets)> 1:
            return self.snippets.pop(0)
        else:
            return None

    def pop_last(self) -> SnippetStructure:
        assert len(self.snippets) == 1

        return self.snippets.pop()

    def __len__(self) -> int:
        return sum(map(lambda x: len(x), self.snippets))


@dataclass(frozen=True)
class CodeLocation:
    path: Path
    line: int