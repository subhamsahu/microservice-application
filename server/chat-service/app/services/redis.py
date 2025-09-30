"""Redis service module"""
import json
import redis.asyncio as redis
from typing import Any, Optional
from app.core.logger import logger
from app.core.config import config

from server_shared.utils.meta_classes import Singleton


class RedisService(metaclass=Singleton):
    """
    Redis service wrapper for async operations.
    Provides helper methods for get/set, publish/subscribe, and caching.
    """

    def __init__(self, url: str = config.REDIS_URL) -> None:
        self.url = url
        self._client: Optional[redis.Redis] = None

    @property
    def client(self) -> redis.Redis | None:
        """Returns redis client"""
        return self._client

    async def connect(self, url: Optional[str] = None, decode_responses: bool = True):
        """
        Establish a connection to Redis with a connection pool.
        """
        if self._client is None:
            self._client = redis.from_url(
                url or self.url,
                encoding="utf-8" if decode_responses else None,
                decode_responses=decode_responses,
                max_connections=20,
            )
            logger.info(f"Connected to Redis at {url or self.url}")
        return self._client

    async def close(self):
        """
        Close Redis connection pool.
        """
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Redis connection closed.")

    async def set(self, key: str, value: Any, expire: int | None = None):
        """
        Set a key-value pair in Redis with optional expiration.
        """
        if not self._client:
            await self.connect()
            
        try:
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            await self._client.set(key, serialized_value, ex=expire)
            logger.debug(f"Set key '{key}' in Redis")
        except Exception as e:
            logger.error(f"Error setting key '{key}' in Redis: {e}")

    async def get(self, key: str) -> Any:
        """
        Get value by key from Redis.
        """
        if not self._client:
            await self.connect()
            
        try:
            value = await self._client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Error getting key '{key}' from Redis: {e}")
            return None

    async def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.
        """
        if not self._client:
            await self.connect()
            
        try:
            result = await self._client.delete(key)
            logger.debug(f"Deleted key '{key}' from Redis")
            return bool(result)
        except Exception as e:
            logger.error(f"Error deleting key '{key}' from Redis: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.
        """
        if not self._client:
            await self.connect()
            
        try:
            result = await self._client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking existence of key '{key}' in Redis: {e}")
            return False

    async def health_check(self) -> bool:
        """
        Perform a health check on Redis connection.
        """
        if not self._client:
            return False
            
        try:
            await self._client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


# Global singleton instance
redis_service = RedisService()