import logging.config
import multiprocessing
import os
from collections import Counter, defaultdict
from fnmatch import fnmatch
from multiprocessing import Queue

import dill as pickle
import shutil
import time
from multiprocessing.pool import Pool
from queue import Empty
from tqdm import tqdm
from typing import List, Tuple, Dict, Iterator

from dataprep.parse.model.placeholders import placeholders
from dataprep.fileutils import read_file_contents
from dataprep.util import AtomicInteger, merge_dicts_, groupify, create_chunk_generator

logger = logging.getLogger(__name__)

queue_size = AtomicInteger()

PARTVOCAB_EXT = 'partvocab'
PARTIAL_VOCABS_READY_FILENAME = 'ready'

VOCABSIZE_FILENAME = 'vocabsize'
VOCAB_FILENAME = 'vocab'

N_CHUNKS = 20
BLOCKING_TIMEOUT_SECONDS_SHORT = 5
BLOCKING_TIMEOUT_SECONDS_LONG = 300
MAX_INIT_PARTIAL_VOCABS = 256 * 20

class PartialVocab(object):
    CLASS_VERSION = '2.0.0'

    def __init__(self, word_counts: Counter, chunk: int):
        if not isinstance(word_counts, Counter):
            raise TypeError(f'Vocab must be a Counter, but is {type(word_counts)}')

        self.merged_word_counts = word_counts
        self.stats = [(1,
                       len(self.merged_word_counts),
                       self.merged_word_counts[placeholders['non_eng']])]
        self.n_files = 1
        self.chunk = chunk
        self.id = self._generate_id()

    def _generate_id(self) -> str:
        return str(os.getpid()) + ''.join(str(time.time()).split('.'))

    def renew_id(self) -> None:
        self.id = self._generate_id()

    def set_path_to_dump(self, path: str) -> None:
        self.path_to_dump = path

    def add_vocab(self, partial_vocab: 'PartialVocab') -> List[str]:
        self.merged_word_counts, new_words = merge_dicts_(self.merged_word_counts, partial_vocab.merged_word_counts)
        cur_vocab_size = len(self.merged_word_counts)

        self.n_files += partial_vocab.n_files
        new_stats_entry = (self.n_files,
                           cur_vocab_size,
                           self.merged_word_counts[placeholders['non_eng']])
        self.stats.extend(partial_vocab.stats + [new_stats_entry])
        return new_words

    def write_stats(self, path_to_stats_file: str) -> None:
        stats = self.__generate_stats()
        with open(path_to_stats_file, 'w') as f:
            vocabsize = int(stats[-1][1][0])
            f.write(f'{vocabsize}\n')
            for percent, (v, n) in stats:
                f.write(f"{percent:.4f} {int(v)} {int(n)}\n")

    def limit_max_vocab(self, vocab_size_threshold: int) -> None:
        sorted_vocab = sorted(self.merged_word_counts.items(), key=lambda x: x[1], reverse=True)
        if vocab_size_threshold > len(sorted_vocab):
            return
        min_freq_excluded = sorted_vocab[vocab_size_threshold][1]
        adjusted_threshold = vocab_size_threshold - 1
        while adjusted_threshold >= 0 and sorted_vocab[adjusted_threshold][1] == min_freq_excluded:
            adjusted_threshold -= 1
        self.merged_word_counts = {k: v for (k, v) in sorted_vocab[:adjusted_threshold + 1]}

    def write_vocab(self, path_to_vocab_file: str) -> None:
        sorted_vocab = sorted(self.merged_word_counts.items(), key=lambda x: x[1], reverse=True)
        _dump_vocab_dict(sorted_vocab, path_to_vocab_file)

    def __generate_stats(self):
        d = defaultdict(list)
        for entry in self.stats:
            d[entry[0]].append(tuple(entry[1:]))
        fin = {(float(k) / self.n_files): tuple([sum(elm) / len(elm) for elm in zip(*v)]) for k, v in d.items()}
        return sorted(fin.items())


class VocabMerger(multiprocessing.Process):
    def __init__(self, id: int, tasks: Dict[int, Queue], path_to_dump: str, process_counter: AtomicInteger,
                 chunk_queue: Queue, merges_left_counter: AtomicInteger,
                 vocab_file_path: str, vocab_size_file_path: str):
        multiprocessing.Process.__init__(self)
        self.id = id
        self.tasks = tasks
        self.path_to_dump = path_to_dump
        self.process_counter = process_counter
        self.chunk_queue = chunk_queue
        self.merges_left_counter = merges_left_counter
        self.total_merges = merges_left_counter.value
        self.vocab_file_path = vocab_file_path
        self.vocav_size_file_path = vocab_size_file_path

    def run(self) -> None:
        while True:
            chunk_assigned = self.chunk_queue.get(block=True, timeout=BLOCKING_TIMEOUT_SECONDS_SHORT)
            if chunk_assigned == -1:
                if not self.process_counter.compare_and_dec(1):
                    logger.debug(
                        f"[{self.id}] No vocabs available for merge. "
                        f"Terminating process..., mergers left: {self.process_counter.value}")
                    break
                else:
                    logger.debug("Leaving 1 process to finish the merges")
                    self._finish_merges()
                    logger.debug(f'[{self.id}] Vocab files are saved. Terminating the process...')
                    break

            first = None
            try:
                first = self.tasks[chunk_assigned].get(block=True, timeout=BLOCKING_TIMEOUT_SECONDS_LONG)
                second = self.tasks[chunk_assigned].get(block=True, timeout=BLOCKING_TIMEOUT_SECONDS_LONG)
            except Empty:
                logger.debug(f"[{self.id}] Could not get a task from queue. Terminating")
                if first:
                    self.tasks[chunk_assigned].put_nowait(first)
                return

            start = time.time()

            merges_left = self.merges_left_counter.get_and_dec()
            merges_done = self.total_merges - merges_left
            log_this_merge = (merges_left & (merges_left - 1) == 0 or merges_done & (merges_done - 1) == 0)
            if log_this_merge:
                logger.info(
                    f'[{self.id}] Merging vocabs ({self.total_merges - merges_left} out of {self.total_merges})')

            first, new_words = self._merge(first, second)

            if log_this_merge:
                self._log_merge_results(new_words, len(first.merged_word_counts), time.time() - start)

            self.tasks[chunk_assigned].put_nowait(first)

    def _finish_merges(self) -> None:
        logger.info("===============     Finishing merges    ===============")
        list_from_chunks = [queue.get(block=True, timeout=BLOCKING_TIMEOUT_SECONDS_SHORT) for queue in
                            self.tasks.values()]

        percents_in_one_chunk = 100 // len(list_from_chunks)

        first = list_from_chunks.pop()
        for i, vocab in enumerate(list_from_chunks):
            logger.info(
                f'{(i+1)* percents_in_one_chunk}% + {percents_in_one_chunk}%  ---> {(i+2) * percents_in_one_chunk}%')

            start = time.time()

            first, new_words = self._merge(first, vocab)

            self._log_merge_results(new_words, len(first.merged_word_counts), time.time() - start)

        first.write_stats(self.vocav_size_file_path)
        first.write_vocab(self.vocab_file_path)
        shutil.rmtree(self.path_to_dump)

    def _log_merge_results(self, new_words: List[str], resulting_vocab_size: int, time: float) -> None:
        logger.debug(f"[{self.id}] New words: {new_words[:10]} ..., total: {len(new_words)}")
        logger.debug(
            f"[{self.id}] Merging took {time:.3f} s, current vocab size: {resulting_vocab_size}")

    def _merge(self, first: PartialVocab, second: PartialVocab) -> Tuple[PartialVocab, List[str]]:
        first_id = first.id
        second_id = second.id

        new_words = first.add_vocab(second)

        first.renew_id()
        path_to_new_file = os.path.join(self.path_to_dump, f'{first_id}_{second_id}_{first.id}.{PARTVOCAB_EXT}')
        pickle.dump(first, open(path_to_new_file, 'wb'))
        finish_file_dumping(path_to_new_file)

        return first, new_words


def get_vocab(file_paths: List[str]) -> Counter:
    vocab = Counter()
    for file in file_paths:
        lines, _ = read_file_contents(file)
        for line in lines:
            vocab.update(line.split(' '))
    return vocab


def create_and_dump_partial_vocab(param: Tuple[List[str], str, int]) -> PartialVocab:
    path_to_file, path_to_dump, chunk = param
    vocab = get_vocab(path_to_file)
    partial_vocab = PartialVocab(vocab, chunk)
    pickle.dump(partial_vocab, open(os.path.join(path_to_dump, f'{partial_vocab.id}.{PARTVOCAB_EXT}'), 'wb'))
    return partial_vocab


def finish_file_dumping(path_to_new_file: str) -> None:
    try:
        pickle.load(open(path_to_new_file, 'rb'))
    except EOFError:
        # file has not been written properly
        os.remove(path_to_new_file)
        return

    dir, base = os.path.split(path_to_new_file)
    spl = base.split('.')[0].split('_')
    if len(spl) != 3:
        raise AssertionError(f'Wrong file: {path_to_new_file}')
    first_id, second_id, new_id = spl[0], spl[1], spl[2]

    first_file = os.path.join(dir, f'{first_id}.{PARTVOCAB_EXT}')
    if os.path.exists(first_file):
        os.remove(first_file)

    second_file = os.path.join(dir, f'{second_id}.{PARTVOCAB_EXT}')
    if os.path.exists(second_file):
        os.remove(second_file)

    new_file = os.path.join(dir, f'{new_id}.{PARTVOCAB_EXT}')
    os.rename(path_to_new_file, new_file)


def list_to_queue(lst: List) -> Queue:
    queue = Queue()
    for elm in lst:
        queue.put_nowait(elm)
    return queue


def create_initial_partial_vocabs(all_files: List[bytes], path_to_dump: str) -> List[PartialVocab]:
    partial_vocabs_queue = []
    file_groups = groupify(all_files, MAX_INIT_PARTIAL_VOCABS)
    file_groups_total = len(file_groups)
    chunk_generator = create_chunk_generator(len(file_groups), N_CHUNKS)
    params = [(file_group, path_to_dump, chunk) for file_group, chunk in zip(file_groups, chunk_generator)]
    pool = Pool()
    partial_vocab_it = pool.imap_unordered(create_and_dump_partial_vocab, params)
    for partial_vocab in tqdm(partial_vocab_it, total=file_groups_total):
        partial_vocabs_queue.append(partial_vocab)
    return partial_vocabs_queue


def create_chunk_queue(chunk_sizes: Dict[int, int], num_mergers: int) -> Tuple[Queue, int]:
    chunk_queue_list = [chunk for chunk, chunk_size in chunk_sizes.items() for _ in range(chunk_size - 1)]
    return list_to_queue(chunk_queue_list + [-1 for _ in range(num_mergers)]), len(chunk_queue_list)


def mapify_tasks(tasks: List[PartialVocab]) -> Tuple[Dict[int, Queue], Dict[int, int]]:
    task_lists_in_chunks = defaultdict(list)
    for task in tasks:
        task_lists_in_chunks[task.chunk].append(task)
    return {chunk: list_to_queue(task_list_in_chunk) for chunk, task_list_in_chunk in
            task_lists_in_chunks.items()}, {k: len(v) for k, v in task_lists_in_chunks.items()}


def load_partial_vocabs(path: str) -> List[PartialVocab]:
    logger.info(f"Loading partially calculated vocabs from {path} ...")
    for file in os.listdir(path):
        if fnmatch(file, f'[0-9]*_[0-9]*_[0-9]*.{PARTVOCAB_EXT}'):
            # hasn't been terminated properly
            finish_file_dumping(os.path.join(path, file))

    task_list = []
    for file in os.listdir(path):
        if file.endswith(PARTVOCAB_EXT):
            part_vocab = pickle.load(open(os.path.join(path, file), 'rb'))
            if not isinstance(part_vocab, PartialVocab):
                raise TypeError(f"Object {str(part_vocab)} must be VocabMerger version {part_vocab.VERSION}")
            task_list.append(part_vocab)

    return task_list


def create_partial_vocabs(file_iterator: Iterator[bytes], path_to_dump: str) -> List[PartialVocab]:
    logger.info(f"Calculating vocabulary from scratch")
    if os.path.exists(path_to_dump):
        shutil.rmtree(path_to_dump)
    os.makedirs(path_to_dump)

    all_files = [file for file in file_iterator]
    if not all_files:
        logger.warning("No preprocessed files found.")
        exit(4)
    task_list = create_initial_partial_vocabs(all_files, path_to_dump)
    open(os.path.join(path_to_dump, PARTIAL_VOCABS_READY_FILENAME), 'a').close()
    return task_list


def partial_vocabs_ready(path_to_dump: str) -> bool:
    return os.path.exists(os.path.join(path_to_dump, PARTIAL_VOCABS_READY_FILENAME))


def _dump_vocab_dict(lst: List[Tuple[str, int]], file: str) -> None:
    with open(file, 'w') as f:
        for word, freq in lst:
            f.write(f'{str(word)}{VOCAB_DICT_DELIM}{freq}\n')


VOCAB_DICT_DELIM = '\t'


def _load_vocab_dict(file) -> Dict[str, int]:
    words = {}
    with open(file, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            splits = line.split(VOCAB_DICT_DELIM)
            words[splits[0]] = int(splits[1])
    return words


def _load_vocab_set(file: str):
    non_bpe_tokens = set()
    with open(file, 'r') as f:
        for line in f:
            non_bpe_tokens.add(line.rstrip('\n'))
    return non_bpe_tokens


def calc_vocab(path: str, file_iterator: Iterator[bytes], output_dir: str):
    vocab_file_path = os.path.join(output_dir, VOCAB_FILENAME)
    vocab_size_file_path = os.path.join(output_dir, VOCABSIZE_FILENAME)
    if os.path.exists(vocab_size_file_path) and os.path.exists(vocab_file_path):
        logger.info(f"Vocab files already exist at: {os.path.dirname(vocab_size_file_path)}/ . Doing nothing.")
        return

    path_to_dump = os.path.join(output_dir, 'part_vocab')

    if partial_vocabs_ready(path_to_dump):
        task_list = load_partial_vocabs(path_to_dump)
    else:
        logger.debug(f"Reading files from: {path}")
        task_list = create_partial_vocabs(file_iterator, path_to_dump)

    n_processes = multiprocessing.cpu_count()
    logger.debug(f"Using {n_processes} mergers, number of partial vocabs: {len(task_list)}")
    tasks_queues, chunk_sizes = mapify_tasks(task_list)
    chunk_queue, merges_to_be_done = create_chunk_queue(chunk_sizes, n_processes)
    logger.debug(f'==================    Starting merging    =================')
    logger.debug(f'Merges need to be done: {merges_to_be_done}')
    process_counter = AtomicInteger(n_processes)
    merges_left_counter = AtomicInteger(merges_to_be_done)
    mergers = [VocabMerger(i + 1, tasks_queues, path_to_dump, process_counter, chunk_queue,
                           merges_left_counter,
                           vocab_file_path=vocab_file_path,
                           vocab_size_file_path=vocab_size_file_path)
               for i in range(n_processes)]
    for merger in mergers:
        merger.start()

    for merger in mergers:
        merger.join()

    logger.info(f"Vocab is available at {vocab_file_path}")
    logger.info(f"Vocab stats is available at {vocab_size_file_path}")
