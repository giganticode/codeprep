import multiprocessing

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


class PriorityCounter(object):
    REMOVED = '<removed-task>'  # placeholder for a removed task

    def __init__(self, d):
        self.counter = itertools.count()
        self.pq = [[-value, next(self.counter), key] for key, value in d.items()]  # list of entries arranged in a heap
        heapify(self.pq)
        self.entry_finder = {entry[2]: entry for entry in self.pq}  # mapping of tasks to entries

    def add(self, pair, to_add):
        'Add a new task or update the priority of an existing task'
        count = next(self.counter)
        to_add = -to_add
        if pair in self.entry_finder:
            entry = self.entry_finder[pair]
            to_add = entry[0] + to_add
            self.remove_task(pair)
        if to_add != 0:
            entry = [to_add, count, pair]
            self.entry_finder[pair] = entry
            heappush(self.pq, entry)

    def remove_task(self, task):
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(task)
        entry[-1] = PriorityCounter.REMOVED

    def pop_pair(self):
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while self.pq:
            priority, count, pair = heappop(self.pq)
            if pair is not PriorityCounter.REMOVED:
                del self.entry_finder[pair]
                return pair
        raise KeyError('pop from an empty priority queue')
