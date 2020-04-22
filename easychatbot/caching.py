from functools import wraps
from werkzeug.contrib.cache import SimpleCache


cache = SimpleCache()


def simple_cache(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        function_name = f.__name__
        if cache.has(function_name):
            result = cache.get(function_name)
        else:
            result = f(*args, **kwargs)
            cache.set(function_name, result)
        return result
    return wrapper