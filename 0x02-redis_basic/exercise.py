#!/usr/bin/env python3
""" Cache class with Redis decorators for counting and history """
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count how many times a method is called"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs of a method"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = method.__qualname__ + ":inputs"
        output_key = method.__qualname__ + ":outputs"
        # Store input
        self._redis.rpush(input_key, str(args))
        # Call the method and store output
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))
        return result
    return wrapper


class Cache:
    def __init__(self):
        """ Initialize Redis client and flush the DB """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
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

def replay(method: Callable):
    """Display the history of calls for a particular method"""
    r = method.__self__._redis  # Access Redis from method's instance
    qualname = method.__qualname__
    inputs_key = f"{qualname}:inputs"
    outputs_key = f"{qualname}:outputs"

    call_count = r.get(qualname)
    if call_count:
        call_count = int(call_count)
    else:
        call_count = 0

    print(f"{qualname} was called {call_count} times:")

    inputs = r.lrange(inputs_key, 0, -1)
    outputs = r.lrange(outputs_key, 0, -1)

    for inp, out in zip(inputs, outputs):
        print(f"{qualname}(*{inp.decode('utf-8')}) -> {out.decode('utf-8')}")
