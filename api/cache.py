"""
Redis Caching Utilities.

Provides caching decorators and utilities for performance optimization.
"""

import json
import hashlib
from typing import Any, Callable, Optional
from functools import wraps

import redis.asyncio as aioredis

from api.config import settings


# Global Redis client
_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """
    Get Redis client instance.

    Returns:
        Redis client
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    return _redis_client


async def close_redis():
    """Close Redis connection."""
    global _redis_client

    if _redis_client:
        await _redis_client.close()
        _redis_client = None


def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from function arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    # Create deterministic key from arguments
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }

    key_string = json.dumps(key_data, sort_keys=True)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()

    return key_hash


def cached(ttl: int = 3600, prefix: str = "cache"):
    """
    Decorator to cache function results in Redis.

    Args:
        ttl: Time to live in seconds (default: 1 hour)
        prefix: Cache key prefix

    Example:
        @cached(ttl=300, prefix="user")
        async def get_user(user_id: str):
            # Expensive operation
            return user_data
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis = await get_redis()

            # Generate cache key
            func_name = f"{func.__module__}.{func.__name__}"
            arg_key = cache_key(*args, **kwargs)
            key = f"{prefix}:{func_name}:{arg_key}"

            # Try to get from cache
            cached_result = await redis.get(key)

            if cached_result is not None:
                # Cache hit
                return json.loads(cached_result)

            # Cache miss - execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await redis.setex(
                key,
                ttl,
                json.dumps(result, default=str)
            )

            return result

        return wrapper
    return decorator


async def invalidate_cache(pattern: str):
    """
    Invalidate cache keys matching pattern.

    Args:
        pattern: Redis key pattern (e.g., "user:*")
    """
    redis = await get_redis()

    # Find matching keys
    keys = []
    async for key in redis.scan_iter(match=pattern):
        keys.append(key)

    # Delete keys
    if keys:
        await redis.delete(*keys)


async def get_cached(key: str, default: Any = None) -> Any:
    """
    Get value from cache.

    Args:
        key: Cache key
        default: Default value if not found

    Returns:
        Cached value or default
    """
    redis = await get_redis()
    value = await redis.get(key)

    if value is None:
        return default

    return json.loads(value)


async def set_cached(key: str, value: Any, ttl: int = 3600):
    """
    Set value in cache.

    Args:
        key: Cache key
        value: Value to cache
        ttl: Time to live in seconds
    """
    redis = await get_redis()
    await redis.setex(key, ttl, json.dumps(value, default=str))


async def delete_cached(key: str):
    """
    Delete value from cache.

    Args:
        key: Cache key to delete
    """
    redis = await get_redis()
    await redis.delete(key)


class CacheManager:
    """Manage cache for specific entities."""

    def __init__(self, prefix: str, ttl: int = 3600):
        """
        Initialize cache manager.

        Args:
            prefix: Cache key prefix
            ttl: Default time to live in seconds
        """
        self.prefix = prefix
        self.ttl = ttl

    def _make_key(self, identifier: str) -> str:
        """Make cache key with prefix."""
        return f"{self.prefix}:{identifier}"

    async def get(self, identifier: str, default: Any = None) -> Any:
        """Get cached value."""
        key = self._make_key(identifier)
        return await get_cached(key, default)

    async def set(self, identifier: str, value: Any, ttl: Optional[int] = None):
        """Set cached value."""
        key = self._make_key(identifier)
        await set_cached(key, value, ttl or self.ttl)

    async def delete(self, identifier: str):
        """Delete cached value."""
        key = self._make_key(identifier)
        await delete_cached(key)

    async def invalidate_all(self):
        """Invalidate all cache entries with this prefix."""
        pattern = f"{self.prefix}:*"
        await invalidate_cache(pattern)


# Pre-configured cache managers
user_cache = CacheManager("user", ttl=1800)  # 30 minutes
project_cache = CacheManager("project", ttl=600)  # 10 minutes
narrative_cache = CacheManager("narrative", ttl=3600)  # 1 hour
