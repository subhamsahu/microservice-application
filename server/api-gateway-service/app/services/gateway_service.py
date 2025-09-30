""""Gateway service module to interact with Redis."""

from typing import List

from app.core.logger import logger
from .redis import redis_service


class GatewayService:
    """Gateway service to manage connections to Redis."""

    def __init__(self):
        self.client = redis_service.client
        self.redis_available = self.client is not None
        if not self.redis_available:
            logger.warning("Redis client is not connected. Gateway service will work with limited functionality.")
            # Initialize in-memory storage as fallback
            self._memory_store = {}
            self._logged_in_users = []

    async def save_user_selected_category(self, key: str, value: str) -> None:
        """Save a user's selected category into Redis or memory."""
        try:
            if self.redis_available:
                await self.client.set(key, value)
                logger.info(f"Category saved to Redis: {key} -> {value}")
            else:
                self._memory_store[key] = value
                logger.info(f"Category saved to memory: {key} -> {value}")
        except Exception as e:
            logger.error(
                f"GatewayService save_user_selected_category() error: {e}"
            )

    async def save_logged_in_user(self, key: str, value: str) -> List[str]:
        """Save a logged-in user into Redis list or memory if not already present."""
        try:
            if self.redis_available:
                if await self.client.lpos(key, value) is None:
                    await self.client.lpush(key, value)
                    logger.info(f"User {value} added to Redis")
                response = await self.client.lrange(key, 0, -1)
                return response
            else:
                if value not in self._logged_in_users:
                    self._logged_in_users.append(value)
                    logger.info(f"User {value} added to memory")
                return self._logged_in_users.copy()
        except Exception as e:
            logger.error(
                f"GatewayService save_logged_in_user() error: {e}")
            return []

    async def get_logged_in_users(self, key: str) -> List[str]:
        """Retrieve all logged-in users from Redis or memory."""
        try:
            if self.redis_available:
                return await self.client.lrange(key, 0, -1)
            else:
                return self._logged_in_users.copy()
        except Exception as e:
            logger.error(
                f"GatewayService get_logged_in_users() error: {e}")
            return []

    async def remove_logged_in_user(self, key: str, value: str) -> List[str]:
        """Remove a logged-in user from Redis list or memory."""
        try:
            if self.redis_available:
                await self.client.lrem(key, 1, value)
                logger.info(f"User {value} removed from Redis")
                return await self.client.lrange(key, 0, -1)
            else:
                if value in self._logged_in_users:
                    self._logged_in_users.remove(value)
                    logger.info(f"User {value} removed from memory")
                return self._logged_in_users.copy()
        except Exception as e:
            logger.error(
                f"GatewayService remove_logged_in_user() error: {e}")
            return []
