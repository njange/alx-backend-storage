#!/usr/bin/env python3
""" Cache class using Redis with get method and type recovery """
import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    def __init__(self):
        """ Initialize Redis client and flush the DB """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """ Store data with a random UUID key """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[bytes, str, int, float, None]:
        """ Retrieve data by key and optionally apply a conversion function """
        value = self._redis.get(key)
        if value is None:
            return None
        if fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str) -> Optional[str]:
        """ Retrieve data and convert to string """
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """ Retrieve data and convert to int """
        return self.get(key, fn=int)
#!/usr/bin/env python3
""" Cache class using Redis with get method and type recovery """
import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    def __init__(self):
        """ Initialize Redis client and flush the DB """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """ Store data with a random UUID key """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[bytes, str, int, float, None]:
        """ Retrieve data by key and optionally apply a conversion function """
        value = self._redis.get(key)
        if value is None:
            return None
        if fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str) -> Optional[str]:
        """ Retrieve data and convert to string """
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """ Retrieve data and convert to int """
        return self.get(key, fn=int)
