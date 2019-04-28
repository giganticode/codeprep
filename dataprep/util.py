import multiprocessing
import os
from datetime import datetime

import threading
from typing import Dict, Tuple, List, Optional
import itertools
from heapq import heappush, heappop, heapify


def insert_separators(subwords, separator):
    return [s for subword in subwords for s in (subword, separator)][:-1]

def create_regex_from_token_list(token_list):
    m = list(map(lambda x:
             x.replace('\\', '\\\\')
                 .replace("^", "\\^")
                 .replace("+", "\+")
                 .replace("|", "\|")
                 .replace("*", "\*")
                 .replace("[", "\[")
                 .replace("]", "\]")
                 .replace("-", "\-")
                 .replace('"', '\\"')
                 .replace('?', "\?")
                 .replace('(', "\(")
                 .replace(')', "\)")
                 .replace(".", "\.")
                 .replace("$", "\$")
                 , token_list))
    return "(" + "|".join(
        m
    ) +")"


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


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AtomicInteger(object):
    def __init__(self, v=0):
        self._lock = threading.Lock()
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


def dump_dict_into_2_columns(dct, file, val_type=str, delim='\t', append=False):
    with open(file, 'w+' if append else 'w') as f:
        lst = dct.items() if isinstance(dct, dict) else dct
        for word, freq in lst:
            value = ' '.join(freq) if val_type == list else str(freq)
            f.write(f'{str(word)}{delim}{value}\n')


def read_dict_from_2_columns(file, val_type=str, delim='\t'):
    words = {}
    with open(file, 'r') as f:
        for line in f:
            line = line[:-1] if line[-1] else line
            splits = line.split(delim)
            if val_type == list:
                second_column = splits[1].split(' ')
            else:
                try:
                    second_column = int(splits[1])
                except:
                    second_column = splits[1]
            words[splits[0]] = second_column
    return words


def read_list(file):
    res = []
    with open(file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            splits = line.split(' ')
            res.append(splits if len(splits) > 1 else splits[0])
    return res


def dump_list(lst, file):
    with open(file, 'w') as f:
        for elm in lst:
            if isinstance(elm, list) or isinstance(elm, tuple):
                f.write(f"{' '.join(elm)}\n")
            else:
                f.write(f"{elm}\n")


def file_mapper(dir, func, extension="java", ignore_prefix="."):
    import os
    if not os.path.exists(dir):
        raise ValueError(f"Directory doesnt exist: {dir}")
    for root, dirs, files in os.walk(dir):
        for file in files:
            if (extension is None or file.endswith(f".{extension}")) and not file.startswith(ignore_prefix):
                ret = func(os.path.join(root, file))
                if ret is not None:
                    yield ret


def get_dir_last_modification(dir):
    mtime = max(os.path.getmtime(root) for root, _, _ in os.walk(dir))
    return datetime.fromtimestamp(mtime)


def get_timestamp_for_folder(path):
    last_modif_time = get_dir_last_modification(path)
    return last_modif_time.strftime("%y-%m-%dT%H-%M-%S")


def get_two_levels_subdirs(dir):
    subdirs = next(os.walk(dir))[1]
    for subdir in subdirs:
        for subsubdir in next(os.walk(os.path.join(dir, subdir)))[1]:
            yield dir, subdir, subsubdir


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