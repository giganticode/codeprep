import multiprocessing
from heapq import heappush, heappop, heapify

import itertools
from typing import Dict, Tuple, List, Optional, Generator


def merge_dicts_(dict1, dict2) -> Tuple[Dict, List]:
    '''
    this method returns modified dict1! and new words are added to the dictionary
    :param dict1:
    :param dict2:
    :return:
    '''
    new_words = []
    for k, v in dict2.items():
        if k not in dict1:
            dict1[k] = v
            new_words.append(k)
        else:
            dict1[k] = dict1[k] + v
    return dict1, new_words


class AtomicInteger(object):
    def __init__(self, v=0):
        self._lock = multiprocessing.Lock()
        self._queue = multiprocessing.Queue()
        for i in range(v):
            self._queue.put(1)

    def inc(self):
        with self._lock:
            self._queue.put(1)
            return self._queue.qsize()

    def dec(self):
        with self._lock:
            self._queue.get()
            return self._queue.qsize()

    def compare_and_dec(self, val):
        with self._lock:
            result = self._queue.qsize() == val
            self._queue.get()
            return result

    def get_and_dec(self):
        with self._lock:
            result = self._queue.qsize()
            self._queue.get()
            return result

    @property
    def value(self):
        with self._lock:
            return self._queue.qsize()

    @value.setter
    def value(self, v):
        with self._lock:
            self._queue = multiprocessing.Queue()
            for i in range(v):
                self._queue.put(1)


class PriorityCounter(object):
    REMOVED = '<removed-task>'  # placeholder for a removed task

    def __init__(self, d: Dict, automatic_count: bool=True):
        self.counter = itertools.count() if automatic_count else None
        self.pq = [[(-value, next(self.counter)) if self.counter else (-value[0], value[1]), key] for key, value in d.items()]  # list of entries arranged in a heap
        heapify(self.pq)
        self.entry_finder = {entry[1]: entry for entry in self.pq}  # mapping of tasks to entries

    def add(self, pair, to_add: int, c: Optional[int]=None):
        'Add a new task or update the priority of an existing task'
        if (self.counter is None) == (c is None):
            raise ValueError("Either counter should be set, or count argument should be passed!")
        count = next(self.counter) if self.counter else c
        to_add = -to_add
        if pair in self.entry_finder:
            entry = self.entry_finder[pair]
            to_add = entry[0][0] + to_add
            self.remove_task(pair)
        if to_add != 0:
            entry = [(to_add, count), pair]
            self.entry_finder[pair] = entry
            heappush(self.pq, entry)

    def remove_task(self, task):
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(task)
        entry[-1] = PriorityCounter.REMOVED

    def pop_pair(self):
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.pq:
            (priority, count), pair = heappop(self.pq)
            if pair is not PriorityCounter.REMOVED:
                del self.entry_finder[pair]
                return pair, -priority
        raise KeyError('pop from an empty priority queue')


import sys
from numbers import Number
from collections import Set, Mapping, deque


# From https://stackoverflow.com/a/30316760:
def getsize(obj):
    zero_depth_bases = (str, bytes, Number, range, bytearray)
    iteritems = 'items'

    def _getsize(obj_0):
        """Recursively iterate to sum size of object & members."""
        _seen_ids = set()

        def inner(obj):
            obj_id = id(obj)
            if obj_id in _seen_ids:
                return 0
            _seen_ids.add(obj_id)
            size = sys.getsizeof(obj)
            if isinstance(obj, zero_depth_bases):
                pass  # bypass remaining control flow and return
            elif isinstance(obj, (tuple, list, Set, deque)):
                size += sum(inner(i) for i in obj)
            elif isinstance(obj, Mapping) or hasattr(obj, iteritems):
                size += sum(inner(k) + inner(v) for k, v in getattr(obj, iteritems)())
            # Check for custom object instances - may subclass above too
            if hasattr(obj, '__dict__'):
                size += inner(vars(obj))
            if hasattr(obj, '__slots__'):  # can have __slots__ with __dict__
                size += sum(inner(getattr(obj, s)) for s in obj.__slots__ if hasattr(obj, s))
            return size

        return inner(obj_0)

    return _getsize(obj)


def is_python_3_6_and_higher():
    python_version = sys.version_info
    return python_version[0] >= 3 and python_version[1] >= 6


def create_chunk_generator(total: int, n_chunks: int) -> Generator[int, None, None]:
    min_elms_in_chunk = total // n_chunks
    for i in range(min_elms_in_chunk):
        for j in range(n_chunks):
            yield j
    for i in range(total % n_chunks):
        yield i


def groupify(all: List, n_chunks: int) -> List[List]:
    groups = [[] for _ in range(n_chunks if len(all) >= n_chunks else len(all))]
    chunk_gen = create_chunk_generator(len(all), n_chunks)
    for elm, label in zip(all, chunk_gen):
        groups[label].append(elm)
    return groups