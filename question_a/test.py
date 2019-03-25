import unittest
from math_utils import overlap


class TestMathUtils(unittest.TestCase):

    def test_overlap(self):
        """ Tests math_utils.overlap function """

        # Test exception raise
        exception_raise_test_cases = [
            [[1, 5], (2, 6)],
            [(1, 5), [6, 8]],
        ]

        for test_case in exception_raise_test_cases:
            with self.assertRaises(ValueError):
                overlap(test_case[0], test_case[1])

        # Test functionality
        test_cases = [
            # line_a, line_b, overlaps
            [(1, 5), (2, 6), True],
            [(1, 5), (6, 8), False],
            [(1, 5), (0, 7), True],
            [(0, 2), (3, 5), False],
            [(0, 4), (3, 5), True],
            [(0, 6), (3, 5), True],
            [(3, 5), (0, 2), False],
            [(3, 5), (0, 4), True],
            [(3, 5), (0, 6), True],
            [(-1, 5), (2, -6), True],
            [(-1, 5), (-2, 6), True],
            [(-1, 5), (2, 6), True],
            [(-1, -5), (2, 6), False],
            [(-1, 5), (2, -6), True],
            [(-1, -5), (2, -6), False],
            [(-1, -5), (2, -4), False],
        ]

        for test_case in test_cases:
            self.assertEqual(
                overlap(test_case[0], test_case[1]), test_case[2]
            )
