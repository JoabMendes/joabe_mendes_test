

## Question C 

Knowing that Python 3.3 has a [LRU Cache decorator](https://docs.python.org/3/library/functools.html#functools.lru_cache) alrery implemented, 
I decided to create a backport version of that library, using this [recipe](http://code.activestate.com/recipes/578078/) as stating point.

This decorator provides a simple integration, with a dynamic api and thread safety.

The referenced recipe and the default implementation of the @functools.lru_cache don't provide a timeout feature and a geo distributon 
identification for the generated caches. My solution added these abilities (See `cache.py`).

Once a function is decorated with [@functools.lru_cache](https://github.com/python/cpython/blob/master/Lib/functools.py), it will provide two injected methods:

```
To help measure the effectiveness of the cache and tune the maxsize parameter, the wrapped function is instrumented with a cache_info() function that returns a named tuple showing hits, misses, maxsize and currsize. In a multi-threaded environment, the hits and misses are approximate.

The decorator also provides a cache_clear() function for clearing or invalidating the cache.
```

These two function enable the cache testing comfortably.

### Adding the timeout parameter to the lru_cache decorator

1. I changed the `lru_cache` function signature to receive a `timeout` argument.

    ```python
    def lru_cache(maxsize=100, typed=False, timeout=None)  # (Line: 99)
    ```
    
    The `int` timeout should be defined in seconds and it's None by the default,
    which will let the maxsize param define when the cache will be cleared.
    
2. I had to calculate the next expiry time based on the timeout parameter

    ```python
    from datetime import datetime, timedelta
    
    # ...
    
    # calculate the next expiry time based on the timeout (Line: 153)
    expire_delta = expire_time = None
    if timeout:
         expire_delta = timedelta(seconds=timeout)
         expire_time = datetime.utcnow() + expire_delta
    ```
3. Inside the function wrapper I created a method to verify if the cache has
expired:

    ```python
    # (Line: 254)
    def verify_cache_expiry():
        """ Verifies if cache has expired and clears it if it did """
        # gives access to global var
        nonlocal expire_time
        nonlocal expire_delta
        now = datetime.utcnow()
        if expire_time <= now:
            # If expire time was reached let's clear the cache and update
            # the expire time
            cache_clear()
            # update the next expiry time based on the timeout
            expire_time = now + expire_delta
    ```
    
    This method verifies if the cache has expired and if did, it calls the 
    cache_clear() functools.lru_cache original method.

    As I had to use the `nonlocal` statement, this decorator only works on python 3. 

4. After defining `verify_cache_expiry()`, I had to call this function inside the existing
wrappers and from `cache_info()`. With that, if the timeout is set, before every cache 
retrieving routine and inspecting (cache_info()), the cache timeout is verified and 
updated.


### Adding the geo distribution id the cache keys

`@functools.lru_cache` uses the wrapped function arguments to generate a cache 
key for each specific set of arguments (Considering the order and type of arguments if typed=True).
My solution for the geo distributed requirement was to create a timezone based 
geo distribution cache. 

As distributed servers might be in different timezones, using this information to
create cache keys (+ the args) makes it possible to have unique keys for different
timezones with the same set of arguments.

This solution limits the geo distribution to the existing timezones, where servers
in the same location/timezone won't be able to apply this feature, unfortunately.


Here is how I implemented that:


1. I changed the `lru_cache` function signature to receive a `geo_distributed` argument.

    ```python
    def lru_cache(maxsize=100, typed=False, timeout=None, geo_distributed=False)
    ```
    
2. The `_make_key` method is responsible to generate the cache keys. I also changed this
method signature to receive the `geo_distributed` flag.

    ```python
    def _make_key(args, kwds, typed, geo_distributed, tuple=tuple, type=type,
                  len=len):
                  
    # I also simplified the signature of the original function removing the parameters I don't need
    
    ```
    
    And for every call of the `make_key` method inside the function wrapper I also 
    specified that argument. 

3. Updated the `_make_key()` method to add the `time.tzname` tuple to the set of arguments
before generating the keys:
    
    ```python
    # ...
    # Line 91
        if geo_distributed:
            return str(key[0]) + '_' + time.tzname[0] + '_' + time.tzname[1]
            
    # ...
    # Line 94
        if geo_distributed:
            key += time.tzname
    ```
    
    `time.tzname` returns a tuple of the local sys timezone, where `time.tzname[0]` is
    the default local timezone name and `time.tzname[1]` is the day light savings time local
    timezone name.

Unfortunately, there's a known issue with `functools.lru_cache` where it doesn't work
when non hashable arguments are passed to the wrapped function.
However there're are existing solutions for that: https://stackoverflow.com/questions/6358481/using-functools-lru-cache-with-dictionary-arguments/44776960.
This fix will be mentioned as a pending improvement of my solution.


### Writing the tests

The test procedures I used to assert my solution followed these routines:

##### Testing lru_cache with timeout

- Decorate a function (f(x)) with `lru_cache` specifying a timeout of 5 seconds.
- Before calling f(x), assert that the cache is empty (This can be done accessing f(x).cache_info())
- Call f(x) with x as 1
- Assert that cache has 1 cache key stored.
- Wait 6 seconds, so the cache can expire.
- Assert that cache has 0 cache keys stored.

The implementation of this routine can be found in `test_lru_cache.CustomLRUCacheTest.test_lru_cache_with_timeout()`.

##### Testing lru_cache with geo_distribution active

- Decorate a function (f(x)) with `lru_cache` specifying the `geo_distributed` as `True`.
- Before calling f(x), assert that the cache is empty (This can be done accessing f(x).cache_info())
- Call f(x) with x as 1
- Assert that cache has 1 cache key stored.
- Change the sys timezone
- Call f(x) with x as 1 again
- Assert that cache has 2 cache keys stored. (Even calling f(x) with the same argument, another key should
be generated because the timezone was changed.

The implementation of this routine can be found in `test_lru_cache.CustomLRUCacheTest.test_lru_cache_with_geo_distribution()`.

Run `./test.sh` from `/question_c` within a python 3 virtual env to execute the tests.

### Possible Improvements


- The current cache timeout specifies the whole cache storage life cycle.
If you define a expiry time of 5 min, the decorator will refresh the whole existing
cache related to the target function every 5min. Since I have access to the make_key 
method, it's possible to associate the timeout for just a specific set of arguments and cache key.
With that, each set of argument will have its unique timeout life cycle.

- Specify a cache key or sufix on the decorator signature.

- Clear cache by cache key or sufix.

- [Accept not hashable keyword arguments](https://stackoverflow.com/questions/6358481/using-functools-lru-cache-with-dictionary-arguments/44776960)

- Add a proper parameter validation


### References

https://en.wikipedia.org/wiki/Geo-replication
https://docs.python.org/3/library/functools.html#functools.lru_cache
http://code.activestate.com/recipes/578078/
https://github.com/python/cpython/blob/master/Lib/functools.py
http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used


