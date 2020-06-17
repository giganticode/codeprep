# SPDX-FileCopyrightText: 2020 2020 Hlib Babii <hlibbabii@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import bisect
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional

from codeprep.util.misc import cum_sum


@dataclass(frozen=True)
class PureSnippetStructure:
    subtokens_in_each_line: List[int]
    _cumulative_sizes: List[int] = field(repr=False, hash=False, compare=False)

    @classmethod
    def of(cls, subtokens_in_each_line: List[int]) -> 'PureSnippetStructure':
        return cls(subtokens_in_each_line, cum_sum(subtokens_in_each_line))

    @classmethod
    def empty(cls) -> 'PureSnippetStructure':
        return cls.of([0])

    @classmethod
    def empty_line(cls) -> 'PureSnippetStructure':
        return cls.of([0, 0])

    def __len__(self) -> int:
        return self._cumulative_sizes[-1]

    def tie_to_working_dir(self, path: Path, first_line: int) -> 'SnippetStructure':
        return SnippetStructure(self.subtokens_in_each_line, self._cumulative_sizes, path, first_line)

    def _merge_lines(self, other: 'PureSnippetStructure') -> Tuple[List[int], List[int]]:
        lines_combines = self.subtokens_in_each_line[:-1] + \
                         [self.subtokens_in_each_line[-1] + other.subtokens_in_each_line[0]] + \
                         other.subtokens_in_each_line[1:]
        cumul = self._cumulative_sizes[:-1] + [x + self._cumulative_sizes[-1] for x in other._cumulative_sizes]
        return lines_combines, cumul

    def merge(self, other: 'PureSnippetStructure') -> 'PureSnippetStructure':
        lines_combines, cumul = self._merge_lines(other)
        return PureSnippetStructure(lines_combines, cumul)

    def _split_lines(self, second_part_start_index: int):
        line_to_be_split = bisect.bisect_right(self._cumulative_sizes, second_part_start_index, 0, len(self._cumulative_sizes))
        total_lengths_of_previous_lines = self._cumulative_sizes[line_to_be_split - 1] if line_to_be_split > 0 else 0
        position_to_split_in_line = second_part_start_index - total_lengths_of_previous_lines

        lines_in_first = self.subtokens_in_each_line[:line_to_be_split]
        cumul_lines_in_first = self._cumulative_sizes[:line_to_be_split]
        if line_to_be_split < len(self.subtokens_in_each_line):
            lines_in_first.append(position_to_split_in_line)
            cumul_lines_in_first.append((cumul_lines_in_first[-1] if cumul_lines_in_first else 0) + position_to_split_in_line)
            first_line_in_second = [self.subtokens_in_each_line[line_to_be_split] - position_to_split_in_line]
        else:
            first_line_in_second = [0]
        lines_in_second = first_line_in_second + self.subtokens_in_each_line[line_to_be_split+1:]
        return lines_in_first, cumul_lines_in_first, lines_in_second

    def split(self, second_part_start_index: int) -> Tuple['PureSnippetStructure', 'PureSnippetStructure']:
        lines_in_first, cumul_lines_in_first, lines_in_second = self._split_lines(second_part_start_index)
        return PureSnippetStructure(lines_in_first, cumul_lines_in_first), PureSnippetStructure.of(lines_in_second)


@dataclass(frozen=True)
class SnippetStructure(PureSnippetStructure):
    """
    >>> snippet_a = SnippetStructure.from_path_and_lines(Path(''), [3], 2)
    >>> snippet_a.split(4)
    (.: [3], first-line: 2, .: [0], first-line: 2)
    >>> snippet_a.split(0)
    (.: [0], first-line: 2, .: [3], first-line: 2)
    >>> snippet_a.split(2)
    (.: [2], first-line: 2, .: [1], first-line: 2)
    >>> snippet_a.split(3)
    (.: [3], first-line: 2, .: [0], first-line: 2)

    >>> snippet_b = SnippetStructure.from_path_and_lines(Path(''), [3, 0, 0, 4], 2)
    >>> len(snippet_b)
    7
    >>> snippet_b.split(3)
    (.: [3, 0, 0, 0], first-line: 2, .: [4], first-line: 5)
    >>> snippet_b.split(7)
    (.: [3, 0, 0, 4], first-line: 2, .: [0], first-line: 5)
    >>> first, second = snippet_b.split(4)
    >>> first
    .: [3, 0, 0, 1], first-line: 2
    >>> len(first)
    4
    >>> second
    .: [3], first-line: 5
    >>> len(second)
    3
    >>> second.merge(first)
    Traceback (most recent call last):
    ...
    ValueError: Snippets are not adjacent.
    >>> third = first.merge(second)
    >>> third
    .: [3, 0, 0, 4], first-line: 2
    >>> third == snippet_b
    True
    >>> len(third)
    7

    """
    path: Path
    first_line: int

    @classmethod
    def from_path_and_lines(cls, path: Path, subtokens_in_each_line: List[int], first_line: int) -> 'SnippetStructure':
        return SnippetStructure(subtokens_in_each_line, cum_sum(subtokens_in_each_line), path, first_line)

    def untie_from_file(self) -> PureSnippetStructure:
        return PureSnippetStructure(self.subtokens_in_each_line, self._cumulative_sizes)

    def merge(self, other: 'SnippetStructure') -> 'SnippetStructure':
        if self.path != other.path:
            raise ValueError("Cannot merge two different files.")

        if self.first_line + len(self.subtokens_in_each_line) - 1 != other.first_line:
            raise ValueError("Snippets are not adjacent.")

        lines, cumul = self._merge_lines(other)
        return SnippetStructure(lines, cumul, self.path, self.first_line)

    def split(self, second_part_start_index: int) -> Tuple['SnippetStructure', 'SnippetStructure']:
        lines1, lines1_cumul, lines2 = self._split_lines(second_part_start_index)

        return SnippetStructure(lines1, lines1_cumul, self.path, self.first_line), \
               SnippetStructure.from_path_and_lines(self.path, lines2, self.first_line + len(lines1) - 1)

    def __len__(self) -> int:
        return len(self.untie_from_file())

    def __repr__(self):
        return f'{self.path}: {self.subtokens_in_each_line}, first-line: {self.first_line}'


@dataclass
class CodeBaseStructure:
    """
    >>> snippet = SnippetStructure.from_path_and_lines(Path(''), [3, 4], 2)
    >>> snippet_a, snippet_b = snippet.split(5)
    >>> prepped_code = CodeBaseStructure.of([snippet_a, snippet_b])
    >>> prepped_code.split(7)
    (CodeBaseStructure(snippets=[.: [3, 2], first-line: 2, .: [2], first-line: 3]), CodeBaseStructure(snippets=[]))
    >>> prepped_code.split(99)
    (CodeBaseStructure(snippets=[.: [3, 2], first-line: 2, .: [2], first-line: 3]), CodeBaseStructure(snippets=[]))
    >>> first, second = prepped_code.split(2)
    >>> first
    CodeBaseStructure(snippets=[.: [2], first-line: 2])
    >>> len(first)
    2
    >>> second
    CodeBaseStructure(snippets=[.: [1, 2], first-line: 2, .: [2], first-line: 3])
    >>> len(second)
    5
    >>> third = first.merge(second)
    >>> third
    CodeBaseStructure(snippets=[.: [3, 4], first-line: 2])
    >>> third = prepped_code
    >>> len(third)
    7

    """
    snippets: List[SnippetStructure]
    _cumulative_sizes: List[int] = field(repr=False, hash=False, compare=False)

    @classmethod
    def empty(cls) -> 'CodeBaseStructure':
        return cls([], [])

    @classmethod
    def of(cls, snippets: List[SnippetStructure]) -> 'CodeBaseStructure':
        return CodeBaseStructure(snippets, cum_sum(map(lambda x: len(x), snippets)))

    def add_snippet(self, prepped_snippet: SnippetStructure) -> 'CodeBaseStructure':
        if not self.snippets or self.snippets[-1].path != prepped_snippet.path:
            self.snippets.append(prepped_snippet)
            self._cumulative_sizes.append(len(self) + len(prepped_snippet))
        else:
            self.snippets[-1] = self.snippets[-1].merge(prepped_snippet)
            self._cumulative_sizes[-1] + len(prepped_snippet)
        return self

    def merge(self, code_base_structure: 'CodeBaseStructure') -> 'CodeBaseStructure':
        for snippet in code_base_structure.snippets:
            self.add_snippet(snippet)
        return self

    def split(self, second_part_start_index: int) -> Tuple['CodeBaseStructure', 'CodeBaseStructure']:
        snippet_to_be_split = bisect.bisect_right(self._cumulative_sizes, second_part_start_index, 0, len(self._cumulative_sizes))
        total_lengths_of_previous_snippets = self._cumulative_sizes[snippet_to_be_split - 1] if snippet_to_be_split > 0 else 0
        position_to_split_in_snippet = second_part_start_index - total_lengths_of_previous_snippets
        if snippet_to_be_split < len(self._cumulative_sizes):
            first, second = self.snippets[snippet_to_be_split].split(position_to_split_in_snippet)
            snippets_in_first = self.snippets[:snippet_to_be_split]
            cumul_length_first = self._cumulative_sizes[:snippet_to_be_split]
            first_code_base_structure = CodeBaseStructure(snippets_in_first, cumul_length_first)
            if len(first) > 0:
                first_code_base_structure.add_snippet(first)
            snippets_in_second = [second] + self.snippets[snippet_to_be_split+1:]
            return first_code_base_structure, CodeBaseStructure.of(snippets_in_second)
        else:
            return CodeBaseStructure(self.snippets, self._cumulative_sizes), CodeBaseStructure.empty()

    def __len__(self) -> int:
        return self._cumulative_sizes[-1] if self._cumulative_sizes else 0


@dataclass(frozen=True)
class CodeLocation:
    path: Path
    line: int