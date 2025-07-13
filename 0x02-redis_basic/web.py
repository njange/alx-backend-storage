#!/usr/bin/env python3
""" Expiring web cache and tracker """
import redis
import requests
from typing import Callable
from functools import wraps

# Initialize Redis connection
redis_client = redis.Redis()


def count_access(method: Callable) -> Callable:
    """Decorator to count how many times a URL is accessed"""
    @wraps(method)
    def wrapper(url: str) -> str:
        redis_client.incr(f"count:{url}")
        return method(url)
    return wrapper


def cache_result(method: Callable) -> Callable:
    """Decorator to cache the result of a URL request for 10 seconds"""
    @wraps(method)
    def wrapper(url: str) -> str:
        key = f"url:{url}"
        cached = redis_client.get(key)
        if cached:
            return cached.decode("utf-8")
        # Call the method and cache the result
        result = method(url)
        redis_client.setex(key, 10, result)  # 10 seconds expiration
        return result
    return wrapper


@count_access
@cache_result
def get_page(url: str) -> str:
    """Get HTML content of a URL (with caching and access counting)"""
    response = requests.get(url)
    return response.text
