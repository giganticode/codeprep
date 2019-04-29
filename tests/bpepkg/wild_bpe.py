import unittest

from dataprep.bpepkg.wild_bpe import run_from_text, are_symmetric, can_be_concat, Side, merge_lists_both, \
    choose_positions_to_merge


def run_and_get_merges(text: str):
    return [(m, occ) for m, occ, _ in run_from_text(text)]


class LearnBpeTest(unittest.TestCase):
    def test_trivial(self):
        merges = run_and_get_merges("a")
        self.assertEqual(merges, [])

    def test_one_merge(self):
        merges = run_and_get_merges("ab")
        self.assertEqual(merges, [("a b", 1)])

    def test_small(self):
        merges = run_and_get_merges("abcdbc")
        self.assertEqual(merges, [("b c", 2), ("a bc", 1), ("abc d", 1), ("abcd bc", 1)])

    def test_same_char_3_times(self):
        merges = run_and_get_merges("aaa")
        self.assertEqual(merges, [("a a", 1), ("aa a", 1)])

    def test_same_char_4_times(self):
        merges = run_and_get_merges("aaaa")
        self.assertEqual(merges, [("a a", 2), ("aa aa", 1)])

    def test_same_char_5_times(self):
        merges = run_and_get_merges("aaaaa")
        self.assertEqual(merges, [("a a", 2), ("aa aa", 1), ('aaaa a', 1)])

    def test_same_char_6_times(self):
        merges = run_and_get_merges("aaaaaa")
        self.assertEqual(merges, [("a a", 3), ("aa aa", 1), ('aaaa aa', 1)])

    def test_same_char_6_times_plus_one(self):
        merges = run_and_get_merges("aaaaaab")
        self.assertEqual(merges, [("a a", 3), ("aa aa", 1), ('aaaa aa', 1), ('aaaaaa b', 1)])

    def test_same_char_8_times(self):
        merges = run_and_get_merges("aaaaaaaa")
        self.assertEqual(merges, [("a a", 4), ("aa aa", 2), ('aaaa aaaa', 1)])

    def test_medium(self):
        merges = run_and_get_merges("there\tis\ta\tthin\ttooth\tin\tthe\ttooth")
        self.assertEqual(merges, [('t h', 5),
                                 ('th e', 2),
                                 ('\t i', 2),
                                 ('n \t', 2),
                                 ('t o', 2),
                                 ('to o', 2),
                                 ('too th', 2),
                                 ('the r', 1),
                                 ('ther e', 1),
                                 ('there \ti', 1),
                                 ('there\ti s', 1),
                                 ('there\tis \t', 1),
                                 ('there\tis\t a', 1),
                                 ('there\tis\ta \t', 1),
                                 ('there\tis\ta\t th', 1),
                                 ('there\tis\ta\tth i', 1),
                                 ('there\tis\ta\tthi n\t', 1),
                                 ('there\tis\ta\tthin\t tooth', 1),
                                 ('there\tis\ta\tthin\ttooth \ti', 1),
                                 ('there\tis\ta\tthin\ttooth\ti n\t', 1),
                                 ('there\tis\ta\tthin\ttooth\tin\t the', 1),
                                 ('there\tis\ta\tthin\ttooth\tin\tthe \t', 1),
                                 ('there\tis\ta\tthin\ttooth\tin\tthe\t tooth', 1)
    ])

    # ------   Inner methods testing

    def test_are_symmetric_True(self):
        self.assertTrue(are_symmetric("abc dcba", "dcba abc"))

    def test_are_symmetric_False(self):
        self.assertFalse(are_symmetric("abc dfe", "efd cba"))

    def test_are_symmetric_different_length(self):
        self.assertFalse(are_symmetric("a c", "ac"))

    def test_can_be_concat_True(self):
        self.assertTrue(can_be_concat("ab cd", "1 ab", Side.LEFT))

    def test_can_be_concat_wrong_side(self):
        self.assertFalse(can_be_concat("ab cd", "1 ab", Side.RIGHT))

    def test_merge_lists_both(self):
        main_list = [0, 5, 7, 11, 16]
        list2 = [1, 9, 15]
        result = merge_lists_both(main_list, list2, (2, -2))
        self.assertEqual(([1, 15], [7]), result)

    def test_merge_lists_both2(self):
        main_list = [2, 7, 10, 12, 15]
        list2 = [1, 3, 6, 11]
        result = merge_lists_both(main_list, list2, (1, -1))
        self.assertEqual(([1, 3, 6], [10]), result)

    def test_merge_lists_both3(self):
        main_list = [0, 2, 4]
        list2 = [1, 3]
        result = merge_lists_both(main_list, list2, (1, -1))
        self.assertEqual(([], [0, 2]), result)

    def test_choose_positions_to_merge(self):
        lst = [0,1,2,5,8,9,10,11,12,20,33,34]

        result = choose_positions_to_merge(lst, 1)
        self.assertEqual(result, ([0,2,5,8,10,12,20,33], [1,9,11,34]))

    def test_choose_positions_to_merge2(self):
        lst = [0]

        result = choose_positions_to_merge(lst, 1)
        self.assertEqual(result, ([0], []))


if __name__ == '__main__':
    unittest.main()
