"""Redis service module"""
import json
from typing import Any, Optional

import redis.asyncio as redis
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
        Set a value in Redis with optional expiration time (in seconds).
        """
        if not self._client:
            raise RuntimeError("Redis is not connected. Call RedisService.connect first.")

        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        await self._client.set(key, value, ex=expire)
        logger.debug(f"Redis SET: {key} -> {value}")

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from Redis. Attempts to JSON-decode if possible.
        """
        if not self._client:
            raise RuntimeError("Redis is not connected. Call RedisService.connect first.")

        value = await self._client.get(key)
        if value is None:
            return None

        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return value

    async def delete(self, key: str):
        """
        Delete a key from Redis.
        """
        if not self._client:
            raise RuntimeError("Redis is not connected. Call RedisService.connect first.")

        await self._client.delete(key)
        logger.debug(f"Redis DEL: {key}")

    async def publish(self, channel: str, message: Any):
        """
        Publish a message to a Redis channel.
        """
        if not self._client:
            raise RuntimeError("Redis is not connected. Call RedisService.connect first.")

        if isinstance(message, (dict, list)):
            message = json.dumps(message)

        await self._client.publish(channel, message)
        logger.debug(f"Redis PUBLISH: {channel} -> {message}")

    async def subscribe(self, channel: str):
        """
        Subscribe to a Redis channel. Returns an async iterator for messages.
        """
        if not self._client:
            raise RuntimeError("Redis is not connected. Call RedisService.connect first.")

        pubsub = self._client.pubsub()
        await pubsub.subscribe(channel)
        logger.info(f"Subscribed to Redis channel: {channel}")
        return pubsub


redis_service = RedisService()
