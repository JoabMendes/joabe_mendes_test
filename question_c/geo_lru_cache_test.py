import unittest
from geo_lru_cache import geo_lru_cache_with_expiry
from time import sleep


class CustomLRUCacheTest(unittest.TestCase):

    def test_geo_lru_cache_with_expiry(self):
        @geo_lru_cache_with_expiry(maxsize=128, expires_in=5)
        def random_function(x):
            return x + 1

        # cache is empty
        self.assertEqual(random_function.cache_info().currsize, 0)
        random_function(1)
        # cache has information
        self.assertEqual(random_function.cache_info().currsize, 1)
        # wait till cache has expired
        sleep(6)
        # cache should be empty again
        self.assertEqual(random_function.cache_info().currsize, 0)
