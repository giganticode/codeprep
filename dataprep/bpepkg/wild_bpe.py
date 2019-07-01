import logging
import os
import sys
from collections import defaultdict
from enum import Enum, auto

import time
from typing import List, Dict, Tuple, Set, Generator, Optional

from dataprep.util import PriorityCounter, getsize

logger = logging.getLogger(__name__)

__version__ = '0.2'


class BpePerformanceStatsEntry(object):
    def __init__(self, merges_done: int, time_for_last_merge: float,
                 n_priority_queue_entries: int,
                 n_index_enties: int,
                 location_index_obj_size: float,
                 neighbour_index_obj_size: float,
                 priority_counter_obj_size: float
                 ):
        self.merges_done = merges_done
        self.time_for_last_merge = time_for_last_merge
        self.n_priority_queue_entries = n_priority_queue_entries
        self.n_index_entries = n_index_enties
        self.location_index_obj_size = location_index_obj_size
        self.neighbour_index_obj_size = neighbour_index_obj_size
        self.priority_counter_obj_size = priority_counter_obj_size


class Side(Enum):
    RIGHT = auto()
    LEFT = auto()

    @staticmethod
    def any():
        return Side.LEFT

    def opposite(self):
        if self.value == Side.LEFT.value:
            return Side.RIGHT
        elif self.value == Side.RIGHT.value:
            return Side.LEFT


def get_char_iterator_for_file(path_to_file: str):
    try:
        yield from get_char_iterator_for_file_with_encoding(path_to_file, 'utf-8')
    except UnicodeDecodeError:
        yield from get_char_iterator_for_file_with_encoding(path_to_file, 'ISO-8859-1')


def escape_char(char: str):
    return '\xA0' if str(char) in [' '] else str(char)


def get_char_iterator_for_file_with_encoding(path_to_file: str, encoding: str) -> Generator[str, None, None]:
    with open(path_to_file, encoding=encoding) as f:
        while True:
            char = f.read(1)
            if char:
                escaped_char = escape_char(char)
                yield escaped_char
            else:
                return


def get_char_iterator_for_dir(path_to_dir: str) -> Generator[str, None, None]:
    for root, dirs, files in os.walk(path_to_dir):
        for file in files:
            if file.endswith('.py'):
                yield from get_char_iterator_for_file(os.path.join(root, file))
                for i in range(3):
                    yield str("\n")


def swap_pair(pair: str) -> str:
    pair_split = pair.split(" ")
    return " ".join([pair_split[1], pair_split[0]])


def are_symmetric(pair1: str, pair2: str):
    if len(pair1) != len(pair2):
        return False
    # TODO make it faster
    split1 = pair1.split(" ")
    split2 = pair2.split(" ")
    return split1[0] == split2[1] and split1[1] == split2[0]


def build_indices(it: Generator[str, None, None]) -> Tuple[Dict[str, List[int]], Dict[str, Dict[Side, Set[str]]]]:
    index = defaultdict(list)
    index_index = defaultdict(lambda: {Side.LEFT: set(), Side.RIGHT: set()})
    first_char = next(it)
    last_key = None
    for i, second_char in enumerate(it):
        key = ' '.join([first_char, second_char])
        index[key].append(i)
        if last_key:
            index_index[last_key][Side.RIGHT].add(key)
            index_index[key][Side.LEFT].add(last_key)
        last_key = key
        first_char = second_char
    return index, index_index


def merge_lists(main_list: List[int], list2: List[int], position_shift: int) -> Tuple[List[int], List[int]]:
    list2_result = []
    result = []
    i = 0; j = 0
    while i < len(main_list) and j < len(list2):
        if main_list[i] + position_shift == list2[j]:
            result.append(min(main_list[i], list2[j]))
            i +=1; j+=1
        elif main_list[i] + position_shift > list2[j]:
            list2_result.append(list2[j])
            j += 1
        else:
            i += 1
    list2_result.extend(list2[j:])
    return list2_result, result


def self_merge(main_list, position_shift):
    result = []
    i = 0
    while i < len(main_list)-1:
        if main_list[i] + position_shift == main_list[i+1]:
            result.append(main_list[i])
            i += 2
        else:
            i += 1
    return [], result


def merge_lists_both(main_list: List[int], list2: List[int], position_shift: Tuple[int, int]) -> Tuple[List[int], List[int]]:
    # position shift should be one positive and one negative number
    if not (position_shift[0] >0 and position_shift[1] < 0):
        raise AssertionError()

    if main_list == list2:
        raise AssertionError("")

    list2_result = []
    result = []
    i = 0; j = 0
    while i < len(main_list)-1 and j < len(list2):
        if main_list[i] + position_shift[0] == list2[j]:
            if main_list[i+1] + position_shift[1] == list2[j]:
                result.append(main_list[i])
            else:
                list2_result.append(list2[j])
            i +=1; j+=1
        elif main_list[i] + position_shift[0] > list2[j]:
            list2_result.append(list2[j])
            j += 1
        else:
            i += 1
    list2_result.extend(list2[j:])
    return list2_result, result


def is_left(main_pair: str, pair2: str):
    right = (pair2.split(" ")[0] == main_pair.split(" ")[1])
    return not right


def merge_pair(pair: str) -> str:
    return "".join(pair.split(" "))


def concat_pairs(main_pair: str, pair2: str, side: Side):
    if not can_be_concat(main_pair, pair2, side):
        raise AssertionError()

    merged_main_pair = merge_pair(main_pair)
    if side.value == Side.LEFT.value:
        return " ".join([pair2.split(" ")[0],merged_main_pair])
    elif side.value == Side.RIGHT.value:
        return " ".join([merged_main_pair, pair2.split(" ")[1]])


def can_be_concat(main_pair: str, pair: str, side: Side):
    if side.value == Side.LEFT.value:
        return main_pair.split(" ")[0] == pair.split(" ")[1]
    elif side.value == Side.RIGHT.value:
        return main_pair.split(" ")[1] == pair.split(" ")[0]


def double_pair(pair: str):
    merged_pair = merge_pair(pair)
    return " ".join([merged_pair, merged_pair])


def calc_position_shift(main_pair: str, pair2: str, side: Side):
    if side.value == Side.LEFT.value:
        return -len(pair2.split(" ")[0])
    elif side.value == Side.RIGHT.value:
        return len(main_pair.split(" ")[0])


def add_pairs_to_neighbour_index(index, pair1, pair2, side, location_index):
    if not can_be_concat(pair1, pair2, side):
        raise AssertionError("")
    if pair2 in location_index:
        index[pair1][side].add(pair2)
        index[pair2][side.opposite()].add(pair1)


def choose_positions_to_merge(main_list, position_shift):
    result_main = []
    result_disappearing = []
    i = 0
    while i < len(main_list)-1:
        result_main.append(main_list[i])
        if main_list[i] + position_shift == main_list[i+1]:
            result_disappearing.append(main_list[i+1])
            i += 1
        i += 1
    if i == len(main_list) -1:
        result_main.append(main_list[i])
    return result_main, result_disappearing


def cleanup_location_index(location_index, most_freq_pair, disappearing_pairs):
    for side in Side:
        for disappearing_pair in disappearing_pairs[side]:
            if len(location_index[disappearing_pair]) == 0:
                del location_index[disappearing_pair]

    if most_freq_pair in location_index:
        # check needed for the case when most freq pair was also a disappearing pair
        del location_index[most_freq_pair]


def cleanup_neighbour_index(location_index, neighbour_index, most_freq_pair):
    for side in Side:
        disappearing_pairs = neighbour_index[most_freq_pair][side]
        for disappearing_pair in disappearing_pairs:
            if disappearing_pair not in location_index and disappearing_pair in neighbour_index:
                del neighbour_index[disappearing_pair]
    del neighbour_index[most_freq_pair]


def update_location_index(location_index, neighbour_index, pair_to_merge):
    occurence_changes = []
    disappearing_pairs = neighbour_index[pair_to_merge]
    main_list = location_index[pair_to_merge]
    if pair_to_merge in neighbour_index[pair_to_merge][Side.any()]:
        main_list, disappearing_pair_list_for_merge_pair = choose_positions_to_merge(
            main_list,
            calc_position_shift(pair_to_merge, pair_to_merge, Side.RIGHT)
        )
    for side in Side:
        for disappearing_pair in disappearing_pairs[side]:
            if pair_to_merge != disappearing_pair:
                disappearing_pair_list = location_index[disappearing_pair]
            elif side.value == Side.RIGHT.value:
                disappearing_pair_list = disappearing_pair_list_for_merge_pair
            else:
                continue


            if can_be_concat(disappearing_pair, pair_to_merge, side) and side.value == Side.RIGHT.value:
                appeared_pair = double_pair(pair_to_merge)
                position_shift = (
                    calc_position_shift(pair_to_merge, disappearing_pair, side),
                    calc_position_shift(pair_to_merge, disappearing_pair, side.opposite())
                )

                disappearing_pair_list, appeared_pairs_locations = merge_lists_both(
                    main_list, disappearing_pair_list, position_shift
                )
                if len(appeared_pairs_locations) > 0:
                    location_index[appeared_pair] = appeared_pairs_locations
                    reduced_occurences = len(location_index[appeared_pair])
                    occurence_changes.append((appeared_pair, appeared_pairs_locations[0], disappearing_pair, disappearing_pair_list[0] if disappearing_pair_list else -1, reduced_occurences))

            appeared_pair = concat_pairs(pair_to_merge, disappearing_pair, side)
            position_shift = calc_position_shift(pair_to_merge, disappearing_pair, side)
            disappearing_pair_list, appeared_pairs_locations = merge_lists(
                main_list, disappearing_pair_list, position_shift
            )
            if len(appeared_pairs_locations) > 0:
                location_index[appeared_pair] = appeared_pairs_locations
                reduced_occurences = len(location_index[appeared_pair])
                occurence_changes.append((appeared_pair, appeared_pairs_locations[0], disappearing_pair, disappearing_pair_list[0] if disappearing_pair_list else -1, reduced_occurences))

            location_index[disappearing_pair] = disappearing_pair_list

    cleanup_location_index(location_index, pair_to_merge, disappearing_pairs)

    return occurence_changes


def update_neighbour_index(location_index, neighbour_index, pair_to_merge):
    for side in Side:
        disappearing_pairs = neighbour_index[pair_to_merge][side]
        for disappearing_pair in disappearing_pairs:
            if can_be_concat(disappearing_pair, pair_to_merge, side):
                appeared_pair = double_pair(pair_to_merge)
                if appeared_pair in location_index:
                    for disappeared_pair2 in disappearing_pairs:
                        mm = concat_pairs(pair_to_merge, disappeared_pair2, side)
                        add_pairs_to_neighbour_index(neighbour_index, appeared_pair, mm, side, location_index)
                        if can_be_concat(pair_to_merge, mm, side.opposite()):
                            mm_concat = concat_pairs(pair_to_merge, mm, side.opposite())
                            add_pairs_to_neighbour_index(neighbour_index, appeared_pair,
                                                         mm_concat, side, location_index)

            appeared_pair = concat_pairs(pair_to_merge, disappearing_pair, side)
            if appeared_pair in location_index:
                for neighbour_of_neighbour in neighbour_index[disappearing_pair][side]:
                    add_pairs_to_neighbour_index(neighbour_index, appeared_pair, neighbour_of_neighbour, side,
                                                 location_index)
                    if can_be_concat(pair_to_merge, neighbour_of_neighbour, side.opposite()):
                        neighbour_of_neighbour_concat = concat_pairs(pair_to_merge, neighbour_of_neighbour,
                                                                     side.opposite())
                        add_pairs_to_neighbour_index(neighbour_index, appeared_pair, neighbour_of_neighbour_concat,
                                                     side, location_index)
                op_side = side.opposite()
                for neighbour_of_neighbour in neighbour_index[pair_to_merge][op_side]:
                    cc = concat_pairs(pair_to_merge, neighbour_of_neighbour, op_side)
                    add_pairs_to_neighbour_index(neighbour_index, appeared_pair, cc, op_side, location_index)
                    if can_be_concat(pair_to_merge, cc, op_side.opposite()):
                        cc_concat = concat_pairs(pair_to_merge, cc, op_side.opposite())
                        add_pairs_to_neighbour_index(neighbour_index, appeared_pair, cc_concat, op_side,
                                                     location_index)

    cleanup_neighbour_index(location_index, neighbour_index, pair_to_merge)


def run(generator: Generator[str, None, None], n_merges: int=sys.maxsize,
        include_performance_stats_every_n_merges: int = 0) \
        -> Tuple[str, int, Optional[List[BpePerformanceStatsEntry]]]:

    checkpoint = time.time()

    location_index, neighbour_index = build_indices(generator)
    priority_counter = PriorityCounter({k: (len(v), v[0]) for k, v in location_index.items()}, automatic_count=False)

    logger.debug(f'Size of location index: {getsize(location_index) / 1e+6} (MB)')
    logger.debug(f'Size of neighbour index: {getsize(neighbour_index) / 1e+6} (MB)')
    logger.debug(f'Index build in : {time.time()-checkpoint} s')

    bpe_performance_stats = None
    if include_performance_stats_every_n_merges:
        bpe_performance_stats = [
            BpePerformanceStatsEntry(
                merges_done=0,
                time_for_last_merge=0,
                n_priority_queue_entries=len(priority_counter.pq),
                n_index_enties=len(location_index),
                location_index_obj_size=getsize(location_index) / 1e+6,
                neighbour_index_obj_size=getsize(neighbour_index) / 1e+6,
                priority_counter_obj_size=getsize(priority_counter) / 1e+6
            )
        ]

    for i in range(n_merges):
        checkpoint = time.time()
        try:
            most_freq_pair, occurences = priority_counter.pop_pair()
            logger.debug(f'Merge {i+1}: {most_freq_pair} {occurences}')
        except KeyError:
            break

        occurence_changes = update_location_index(location_index, neighbour_index, most_freq_pair)
        for (appeared_pair, first_appeared_pair, disappearing_pair, first_left_disappering_pair, n_occurences) in occurence_changes:
            priority_counter.add(appeared_pair, n_occurences, first_appeared_pair)
            if disappearing_pair != most_freq_pair:
                priority_counter.add(disappearing_pair, -n_occurences, first_left_disappering_pair)
            else:
                occurences -= n_occurences

        update_neighbour_index(location_index, neighbour_index, most_freq_pair)

        time_per_merge = time.time() - checkpoint
        if include_performance_stats_every_n_merges > 0 and (i == 1 or i % include_performance_stats_every_n_merges == 0):
            n_index_entries = len(location_index)
            n_priority_queue_entries = len(priority_counter.pq)
            location_index_obj_size = getsize(location_index) / 1e+6
            neighbour_index_obj_size = getsize(neighbour_index) / 1e+6
            priority_queue_obj_size = getsize(priority_counter) / 1e+6

            logger.debug(f"---------------------------  After merge {i}")
            logger.debug(f"Last merge was done in {time_per_merge} s")
            logger.debug(f'The number of keys in the index: {n_index_entries}')
            logger.debug(f'Length of pq {n_priority_queue_entries}')
            logger.debug(f'Size of location index: {location_index_obj_size} (MB)')
            logger.debug(f'Size of neighbour index: {neighbour_index_obj_size} (MB)')
            logger.debug(f'Size of priority counter: {priority_queue_obj_size} (MB)')

            bpe_performance_stats.append(
                BpePerformanceStatsEntry(
                    merges_done=i,
                    time_for_last_merge=time_per_merge,
                    n_priority_queue_entries=n_priority_queue_entries,
                    n_index_enties=n_index_entries,
                    location_index_obj_size=location_index_obj_size,
                    neighbour_index_obj_size=neighbour_index_obj_size,
                    priority_counter_obj_size=priority_queue_obj_size
                )
            )

        yield (most_freq_pair, occurences, bpe_performance_stats)

        if include_performance_stats_every_n_merges > 0 and (location_index_obj_size + neighbour_index_obj_size + priority_queue_obj_size) > 3072:
            return


def run_from_file(path_to_file: str, n_merges: int=sys.maxsize) -> Tuple[str, int, Optional[List[BpePerformanceStatsEntry]]]:
    it = get_char_iterator_for_file(path_to_file)
    return run(it, n_merges)


def run_from_dir(path_to_dir: str, n_merges: int=sys.maxsize) -> Tuple[str, int, Optional[List[BpePerformanceStatsEntry]]]:
    it = get_char_iterator_for_dir(path_to_dir)
    return run(it, n_merges)


def run_from_text(text: str, n_merges: int=sys.maxsize) -> Tuple[str, int, Optional[List[BpePerformanceStatsEntry]]]:
    return run(iter(text), n_merges)


if __name__ == '__main__':
    pass