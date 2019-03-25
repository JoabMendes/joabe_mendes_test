"""

Implements a backport version of the Python 3.3 functools.lru_cache
with cache timeout and geo_distribution by timezone

@author: Joabe Mendes <joabe.mdl@gmail.com>

Implemented from the recipe: http://code.activestate.com/recipes/578078/

References:
https://github.com/python/cpython/blob/master/Lib/functools.py

"""

from collections import namedtuple
from functools import update_wrapper
from threading import RLock
from datetime import datetime, timedelta
import time

_CacheInfo = namedtuple("CacheInfo", ["hits", "misses", "maxsize", "currsize"])


class _HashedSeq(list):
    """
    This class guarantees that hash() will be called no more than once
    per element.  This is important because the lru_cache() will hash
    the key multiple times on a cache miss.
    """
    __slots__ = 'hashvalue'

    def __init__(self, tup, hash=hash):
        """
        :param tup: tuple to be hashed
        :param hash: hash method to be used

        @todo: consider not hashable entries in this class

        """
        self[:] = tup
        self.hashvalue = hash(tup)

    def __hash__(self):
        return self.hashvalue


def _make_key(args, kwds, typed, geo_distributed, tuple=tuple, type=type,
              len=len):
    """
    Make a cache key from optionally typed positional and keyword arguments
    The key is constructed in a way that is flat as possible rather than
    as a nested structure that would take more memory.
    If there is only a single argument and its data type is known to cache
    its hash value, then that argument is returned without a wrapper.  This
    saves space and improves lookup speed.


    :param tuple args: the function args to generate the key with
    :param tuple kwds: the function kwds to generate the key
    :param bool typed: if the args of different types will be cached separately
    :param bool geo_distributed: if timezone should be added to the cache key
    :param class tuple: tuple class to use, you can specify a custom version
    :param def type: type method to use, you can specify a custom version
    :param def len: len method to use, you can specify a custom version
    :return: str/int hash to be used as cache key


    @todo: consider not hashable entries in this class

    """
    # All of code below relies on kwds preserving the order input by the user.
    # Formerly, we sorted() the kwds before looping.  The new way is *much*
    # faster; however, it means that f(x=1, y=2) will now be treated as a
    # distinct call from f(y=2, x=1) which will be cached separately.

    # ensures that keyword arguments cannot be confused with
    # positional arguments
    kwd_mark = (object(),)
    # the simple types that don't need to be hashed
    fasttypes = {int, str}
    key = args
    if kwds:
        key += kwd_mark
        for item in kwds.items():
            key += item
    if typed:
        key += tuple(type(v) for v in args)
        if kwds:
            key += tuple(type(v) for v in kwds.values())
    elif len(key) == 1 and type(key[0]) in fasttypes:
        if geo_distributed:
            return str(key[0]) + '_' + time.tzname[0] + '_' + time.tzname[1]
        return key[0]
    if geo_distributed:
        key += time.tzname
    return _HashedSeq(key)


def lru_cache(maxsize=100, typed=False, timeout=None, geo_distributed=False):
    """
    Least-recently-used cache decorator.


    If *maxsize* is set to None, the LRU features are disabled and the cache
    can grow without bound.

    If *typed* is True, arguments of different types will be cached separately.
    For example, f(3.0) and f(3) will be treated as distinct calls with
    distinct results.

    *timeout* defines the cache life cycle

    If *geo_distributed* is

    Arguments to the cached function must be hashable.

    View the cache statistics named tuple (hits, misses, maxsize, currsize)
    with f.cache_info().  Clear the cache and statistics with f.cache_clear().
    Access the underlying function with f.__wrapped__.

    See:  http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used


    :param int maxsize: maxsize of the cache limit
    :param bool typed: if arguments of different types will be cached
    separately. For example, f(3.0) and f(3) will be treated as distinct calls
    with distinct results.
    :param timeout: seconds to define the cache cicle (Default: None)
    :param bool geo_distributed: if timezone should be added to the cache key
    :return: the decorated function

    """

    # Users should only access the lru_cache through its public API:
    #       cache_info, cache_clear, and f.__wrapped__
    # The internals of the lru_cache are encapsulated for thread safety and
    # to allow the implementation to change (including a possible C version).

    def decorating_function(user_function):

        cache = dict()
        stats = [0, 0]  # make statistics updateable non-locally
        HITS, MISSES = 0, 1  # names for the stats fields
        make_key = _make_key
        cache_get = cache.get  # bound method to lookup key or return None
        _len = len  # localize the global len() function
        lock = RLock()  # because linkedlist updates aren't threadsafe
        root = []  # root of the circular doubly linked list
        root[:] = [root, root, None, None]  # initialize by pointing to self
        nonlocal_root = [root]  # make updateable non-locally
        PREV, NEXT, KEY, RESULT = 0, 1, 2, 3  # names for the link fields
        # calculate the next expiry time based on the timeout
        expire_delta = expire_time = None
        if timeout:
            expire_delta = timedelta(seconds=timeout)
            expire_time = datetime.utcnow() + expire_delta

        if maxsize == 0:

            def wrapper(*args, **kwds):
                if timeout:
                    verify_cache_expiry()
                # no caching, just do a statistics update
                # after a successful call
                result = user_function(*args, **kwds)
                stats[MISSES] += 1
                return result

        elif maxsize is None:

            def wrapper(*args, **kwds):
                if timeout:
                    verify_cache_expiry()
                # simple caching without ordering or size limit
                key = make_key(args, kwds, typed, geo_distributed)
                # root used here as a unique not-found sentinel
                result = cache_get(key, root)
                if result is not root:
                    stats[HITS] += 1
                    return result
                result = user_function(*args, **kwds)
                cache[key] = result
                stats[MISSES] += 1
                return result

        else:

            def wrapper(*args, **kwds):
                if timeout:
                    verify_cache_expiry()
                # size limited caching that tracks accesses by recency
                key = make_key(args, kwds, typed, geo_distributed)
                with lock:
                    link = cache_get(key)
                    if link is not None:
                        # record recent use of the key by
                        # moving it to the front of the list
                        root, = nonlocal_root
                        link_prev, link_next, key, result = link
                        link_prev[NEXT] = link_next
                        link_next[PREV] = link_prev
                        last = root[PREV]
                        last[NEXT] = root[PREV] = link
                        link[PREV] = last
                        link[NEXT] = root
                        stats[HITS] += 1
                        return result
                result = user_function(*args, **kwds)
                with lock:
                    root, = nonlocal_root
                    if key in cache:
                        # getting here means that this same key was added to
                        # the cache while the lock was released. since the link
                        # update is already done, we need only return the
                        # computed result and update the count of misses.
                        pass
                    elif _len(cache) >= maxsize:
                        # use the old root to store the new key and result
                        oldroot = root
                        oldroot[KEY] = key
                        oldroot[RESULT] = result
                        # empty the oldest link and make it the new root
                        root = nonlocal_root[0] = oldroot[NEXT]
                        oldkey = root[KEY]
                        # oldvalue = root[RESULT]
                        root[KEY] = root[RESULT] = None
                        # now update the cache dictionary for the new links
                        del cache[oldkey]
                        cache[key] = oldroot
                    else:
                        # put result in a new link at the front of the list
                        last = root[PREV]
                        link = [last, root, key, result]
                        last[NEXT] = root[PREV] = cache[key] = link
                    stats[MISSES] += 1
                return result

        def cache_info():
            """Report cache statistics"""
            if timeout:
                verify_cache_expiry()
            with lock:
                return _CacheInfo(stats[HITS], stats[MISSES], maxsize,
                                  len(cache))

        def cache_clear():
            """Clear the cache and cache statistics"""
            with lock:
                cache.clear()
                root = nonlocal_root[0]
                root[:] = [root, root, None, None]
                stats[:] = [0, 0]

        def verify_cache_expiry():
            """ Verifies if cache has expired and clears it if it did """
            # gives access to global var
            nonlocal expire_time
            nonlocal expire_delta
            now = datetime.utcnow()
            if expire_time <= now:
                # If expire time was reached let's clear the cache and update
                # the expire time
                # print("Erasing cache")
                cache_clear()
                # update the next expiry time based on the timeout
                expire_time = now + expire_delta

        wrapper.__wrapped__ = user_function
        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return update_wrapper(wrapper, user_function)

    return decorating_function
