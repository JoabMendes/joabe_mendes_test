import unittest
from version_utils import is_version_gt


class TestVersionUtils(unittest.TestCase):

    def test_is_version_gt(self):
        """ Tests version.is_version_gt function """

        # Test exception raise
        exception_raise_value_error_test_cases = [
            [6, 8],
            ["1.2", 8],
            [8, "1.2"],
            ["1.2", "potato"],
            ["potato", "1.1"],
            ["1.1", ""]
        ]

        for test_case in exception_raise_value_error_test_cases:
            with self.assertRaises(ValueError):
                is_version_gt(test_case[0], test_case[1])

        # Test functionality
        test_cases = [
            # version_a, version_b, result
            ["1.2", "1.1", 1],
            ["1.1", "1.2", -1],
            ["1.2", "1.2", 0],
            ["1.1.1", "1.2", -1],
            ["1.2", "1.1.1", 1],
            ["1.1.1", "1.1.1", 0],
            ["1.2.1", "1.2.10", -1],
            ["1.2.10", "1.2.1", 1],
            ["1.1.10", "1.2.10", -1],
            # mixed strings
            ["Version 1.2", " Version 1.1", 1],
            ["Version 1.1", "Version 1.2", -1],
            ["Version 1.2", "Version 1.2", 0],
            ["Version 1.1.1", "Version 1.2", -1],
            ["Version 1.2", "Version 1.1.1", 1],
            ["Version 1.2.1", "Version 1.2.10", -1],
            ["Version 1.2.10", "Version 1.2.1", 1],
            ["Version 1.1.10", "Version 1.2.10", -1],
            ["1.2 Version", "1.1 Version", 1],
            ["1.1 Version", "1.2 Version", -1],
            ["1.2 Version", "1.2 Version", 0],
            ["1.1.1 Version", "1.2 Version", -1],
            ["1.2 Version", "1.1.1 Version", 1],
            ["1.2.1 Version", "1.2.10 Version", -1],
            ["1.2.10 Version", "1.2.1 Version", 1],
            ["1.1.10 Version", "1.2.10 Version", -1],
            ["1.1.10potato", "1.2.10potato", -1],
            ["1.1.potato", "1.2.10potato", -1],
        ]

        for test_case in test_cases:
            self.assertEqual(
                is_version_gt(test_case[0], test_case[1]), test_case[2]
            )
