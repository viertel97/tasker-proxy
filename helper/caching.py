import time
from functools import lru_cache


def ttl_cache(ttl: int, maxsize: int = 128):
	"""
	Time aware lru caching
	"""

	def wrapper(func):
		@lru_cache(maxsize)
		def inner(__ttl, *args, **kwargs):
			# Note that __ttl is not passed down to func,
			# as it's only used to trigger cache miss after some time
			return func(*args, **kwargs)

		return lambda *args, **kwargs: inner(time.time() // ttl, *args, **kwargs)

	return wrapper
