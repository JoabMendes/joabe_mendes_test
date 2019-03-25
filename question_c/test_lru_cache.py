import unittest
from cache import lru_cache
from time import sleep
import time
import os


class CustomLRUCacheTest(unittest.TestCase):

    def test_lru_cache_with_timeout(self):
        @lru_cache(timeout=5)
        def random_function(x):
            return x + 1

        # cache should be empty
        self.assertEqual(random_function.cache_info().currsize, 0)
        random_function(1)
        # cache should have information
        self.assertEqual(random_function.cache_info().currsize, 1)
        # wait till cache has expired
        sleep(6)
        # cache should be empty again
        self.assertEqual(random_function.cache_info().currsize, 0)

    def change_timezone(self):
        if time.tzname == ('GMT', 'BST'):
            # If timezone is Europe/London set it America/Toronto
            os.environ['TZ'] = 'America/Toronto'
            time.tzset()
        else:
            # If not, set it to Europe/London
            os.environ['TZ'] = 'Europe/London'
            time.tzset()

    def test_lru_cache_with_geo_distribution(self):

        @lru_cache(geo_distributed=True)
        def random_function(x):
            return x + 1

        # cache should be empty
        self.assertEqual(random_function.cache_info().currsize, 0)
        random_function(1)
        # cache should have information
        self.assertEqual(random_function.cache_info().currsize, 1)
        # chance the sys timezone
        self.change_timezone()
        # Call the function again with same params to generate another
        # key for this timezone
        random_function(1)
        # Another extra cache should have been generated since we
        # are in another timezone
        self.assertEqual(random_function.cache_info().currsize, 2)

    def test_lru_cache_with_timeout_multiple_args(self):
        """ This test will trigger _make_key to generate a hash """
        @lru_cache(timeout=5)
        def random_function(x, y):
            return x + y

        # cache should be empty
        self.assertEqual(random_function.cache_info().currsize, 0)
        random_function(1, 2)
        # cache should have information
        self.assertEqual(random_function.cache_info().currsize, 1)
        # wait till cache has expired
        sleep(6)
        # cache should be empty again
        self.assertEqual(random_function.cache_info().currsize, 0)

    def test_lru_cache_with_geo_distribution_multiple_args(self):
        """ This test will trigger _make_key to generate a hash """
        @lru_cache(geo_distributed=True)
        def random_function(x, y):
            return x + y

        # cache should be empty
        self.assertEqual(random_function.cache_info().currsize, 0)
        random_function(1, 2)
        # cache should have information
        self.assertEqual(random_function.cache_info().currsize, 1)
        # chance the sys timezone
        self.change_timezone()
        # Call the function again with same params to generate another
        # key for this timezone
        random_function(1, 2)
        # Another extra cache should have been generated since we
        # are in another timezone
        self.assertEqual(random_function.cache_info().currsize, 2)
