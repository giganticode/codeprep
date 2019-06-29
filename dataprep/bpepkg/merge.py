import copy

from typing import List, Tuple, Union, Optional, Iterator, Dict

from dataprep.util import is_python_3_6_and_higher


class Merge(object):
    def __init__(self, pair: Tuple[str, str], freq: int = None, priority: int = None):
        self.pair = pair
        self.freq = freq
        self.priority = priority
    
    @classmethod
    def parse_file_entry(cls, line: str, priority: int) -> "Merge":
        try:
            spl = line.split(" ")
            if len(spl) == 2:
                return cls((spl[0], spl[1]), priority=priority)
            else:
                return cls((spl[0], spl[1]), freq=int(spl[2]), priority=priority)
        except (IndexError, TypeError) as err:
            raise ValueError(f"Invalid merge entry format: {line}", err)
            
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f'{self.pair}: ({self.freq}, {self.priority})'

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.pair == other.pair and self.priority == other.priority \
               and self.freq == other.freq

    def __hash__(self):
        return hash((self.pair, self.priority, self.freq))


class MergeList():
    def __init__(self):
        self.merges: Dict[Tuple[str, str], Merge] = {}

    def __contains__(self, item):
        return item in self.merges

    def __len__(self):
        return len(self.merges)

    def __iter__(self) -> Iterator[Merge]:
        return iter(self._get_sorted_merges())

    def _get_sorted_merges(self) -> List[Merge]:
        if not is_python_3_6_and_higher():
            # we cannot rely on dict order for python versions lower than 3.6
            raise NotImplementedError()

        return list(self.merges.values())

    def __add__(self, other: 'MergeList'):
        if self.__class__ != other.__class__:
            raise TypeError(f"Cannot add {other.__class__} to a MergeList")

        new_merge_list = copy.deepcopy(self)
        first_list_len = len(new_merge_list)
        for merge in other:
            merge.priority += first_list_len
            new_merge_list.append(merge)

        return new_merge_list

    def append(self, merge: Merge) -> 'MergeList':
        # along with the pair we save its priority and the number of its occurrences
        if merge.priority is None:
            merge.priority = len(self.merges)
        elif merge.priority != len(self.merges):
            raise ValueError(f"It's only possible to add merges in priority order. "
                             f"The priority of the next merge should be {len(self.merges)} but is {merge.priority}")

        self.merges[merge.pair] = merge
        return self

    def get_priority(self, pair: Tuple[str, str]) -> int:
        return self.merges[pair].priority

    def __getitem__(self, item) -> Union[List[Merge], Merge]:
        lst = self._get_sorted_merges()
        return lst[item]

    def __repr__(self):
        return repr(self[:])

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self[:] == other[:]


def read_merges(file: str, n_merges: Optional[int] = None) -> MergeList:
    merges = MergeList()
    with open(file, 'r') as f:
        for idx, line in enumerate(f):
            if n_merges and idx >= n_merges:
                break
            line = line.rstrip('\n')
            merges.append(Merge.parse_file_entry(line, idx))
    return merges


def dump_merges(merges: MergeList, file: str):
    with open(file, 'w') as f:
        for merge in merges:
            f.write(f"{' '.join(merge.pair)} {merge.freq}\n")
