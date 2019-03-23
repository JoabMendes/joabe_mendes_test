from datetime import datetime, timedelta
import functools


def geo_lru_cache_with_expiry(**my_kwargs):

    def _wrapper(func):
        # Get the decorator args
        maxsize = my_kwargs.pop('maxsize', 128)
        typed = my_kwargs.pop('typed', False)
        expire_seconds = my_kwargs.pop('expires_in', 300)
        # calculate the expire time
        expire_delta = timedelta(seconds=expire_seconds)
        expire_time = datetime.utcnow() + expire_delta
        # Set the cache to func
        func = functools.lru_cache(maxsize=maxsize, typed=typed)(func)

        @functools.wraps(func)
        def _wrapped(*args, **kwargs):
            # Here I call the function wrapped in my special cache
            # I can clear the cache if I see that the expire time was reached
            # I do that by calling verify_cache_expiry
            verify_cache_expiry()
            return func(*args, **kwargs)

        def verify_cache_expiry():
            """ Verifies if cache has expired and clears it if it did """
            nonlocal expire_time  # gives access to global var
            nonlocal expire_delta  # gives access to global var
            now = datetime.utcnow()
            if expire_time <= now:
                # If expire time was reached let clear the cache and update
                # the expire time
                func.cache_clear()
                expire_time = now + expire_delta

        # lru_cache has a function that returns the cache statistics,
        # lets update this function to also call verify_cache_expiry

        def cache_info():
            verify_cache_expiry()
            return func.cache_info()

        # Gives super access to this wrapper
        _wrapped.cache_info = cache_info
        _wrapped.cache_clear = func.cache_clear
        return _wrapped

    return _wrapper
