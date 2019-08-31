import random

from typing import List

from dataprep.bpepkg import wild_bpe
from dataprep.bpepkg.wild_bpe import BpePerformanceStatsEntry, run


def gen_performance_test_case(data_size_mb: float, entropy: int):
    char_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for i in range(int(data_size_mb * (2 ** 20))):
        w = random.choice(char_list[:2 ** entropy])
        for i in range(len(w)):
            yield w[i]


def plotting_function(data_size_mb: float, entropy: int, version: str,
                      performance_stats: List[BpePerformanceStatsEntry],
                      final_show: bool = True):
    merges_done = list(map(lambda p: p.merges_done, performance_stats))
    n_pq_entries = list(map(lambda p: p.n_priority_queue_entries, performance_stats))
    n_index_entries = list(map(lambda p: p.n_index_entries, performance_stats))
    location_index_obj_size = list(map(lambda p: p.location_index_obj_size, performance_stats))
    neighbour_index_obj_size = list(map(lambda p: p.neighbour_index_obj_size, performance_stats))
    priority_counter_obj_size = list(map(lambda p: p.priority_counter_obj_size, performance_stats))
    total_index_size = [a + b + c for a, b, c in
                        zip(location_index_obj_size, neighbour_index_obj_size, priority_counter_obj_size)]
    merge_time = list(map(lambda p: p.time_for_last_merge, performance_stats))

    import matplotlib.pyplot as plt
    fig, splots = plt.subplots(nrows=3)
    splots[0].plot(merges_done, n_pq_entries, label='priority counter')
    splots[0].plot(merges_done, n_index_entries, label='indices')
    splots[0].set(ylabel='entries',
                  title=f'Wild BPE version {version}, Data size: {data_size_mb} MB, entropy: {entropy} bit')
    splots[0].legend(loc='upper right')

    splots[1].plot(merges_done, location_index_obj_size, label='location index')
    splots[1].plot(merges_done, neighbour_index_obj_size, label='neighbour index')
    splots[1].plot(merges_done, priority_counter_obj_size, label='priority counter')
    splots[1].plot(merges_done, total_index_size, label='total')
    splots[1].set(xlabel='number of merges', ylabel='memory consumed (MB)')
    splots[1].legend(loc='upper right')

    splots[2].plot(merges_done, merge_time)
    splots[2].set(xlabel='number of merges', ylabel='time per merge (s)')

    fig.savefig(f'{version}_{data_size_mb}_{entropy}bit.png')
    if final_show:
        plt.show()


def test_performance():
    test_cases = [
        {'mb': 0.05, 'entropy': 1},
        {'mb': 0.05, 'entropy': 2},
        {'mb': 0.05, 'entropy': 3},
        {'mb': 0.5, 'entropy': 1},
        {'mb': 0.5, 'entropy': 2},
        {'mb': 0.5, 'entropy': 3},
        {'mb': 5, 'entropy': 1},
        {'mb': 5, 'entropy': 2},
        {'mb': 5, 'entropy': 3},
    ]
    stats_every_n = 50

    for test_case in test_cases:
        gen = run(gen_performance_test_case(test_case['mb'], test_case['entropy']), include_performance_stats_every_n_merges=stats_every_n)
        for i in range(1000):
            try:
                merge, occurences, stats = next(gen)
            except StopIteration:
                pass
        plotting_function(test_case['mb'], test_case['entropy'], wild_bpe.__version__, stats)


if __name__ == '__main__':
    test_performance()