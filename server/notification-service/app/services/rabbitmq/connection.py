"""
Singleton RabbitMQ Connection Manager for Notification Service
"""
from typing import Optional
import asyncio
import signal

from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustChannel, AbstractRobustConnection
from aio_pika.exceptions import AMQPConnectionError

from app.core.config import config
from app.core.logger import logger
from server_shared.utils.meta_classes import Singleton


class RabbitMQManager(metaclass=Singleton):
    """
    Singleton RabbitMQ connection manager.
    """
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._connection: Optional[AbstractRobustConnection] = None
            self._channel: Optional[AbstractRobustChannel] = None
            self._connected = False
            self._initialized = True
    
    @property
    def channel(self) -> Optional[AbstractRobustChannel]:
        """Get the RabbitMQ channel instance."""
        return self._channel
    
    @property
    def connection(self) -> Optional[AbstractRobustConnection]:
        """Get the RabbitMQ connection instance."""
        return self._connection
    
    async def initialize(self) -> bool:
        """Initialize RabbitMQ connection."""
        if self._channel is not None and self._connected:
            return True
            
        if not config.RABBITMQ_ENDPOINT:
            logger.error("RabbitMQ endpoint is not configured.")
            return False

        try:
            self._connection = await connect_robust(config.RABBITMQ_ENDPOINT)
            self._channel = await self._connection.channel()
            self._connected = True
            
            logger.info("RabbitMQ connection established successfully.")
            return True
            
        except AMQPConnectionError as error:
            logger.error(f"Failed to connect to RabbitMQ: {error}")
            self._connected = False
            return False
        except Exception as error:
            logger.error(f"Unexpected error in RabbitMQ initialization: {error}")
            self._connected = False
            return False
    
    async def close(self):
        """Close RabbitMQ connection."""
        try:
            if self._channel:
                await self._channel.close()
                logger.info("RabbitMQ channel closed.")
                
            if self._connection:
                await self._connection.close()
                logger.info("RabbitMQ connection closed.")
                
        except Exception as error:
            logger.error(f"Error during RabbitMQ shutdown: {error}")
        finally:
            self._channel = None
            self._connection = None
            self._connected = False
    
    def is_connected(self) -> bool:
        """Check if RabbitMQ is connected."""
        return (self._connected and 
                self._connection is not None and 
                not self._connection.is_closed)


# Global singleton instance
rabbitmq_manager = RabbitMQManager()


# Legacy compatibility functions
async def create_rabbitmq_channel() -> Optional[AbstractRobustChannel]:
    """
    Legacy function for backward compatibility.
    Initializes RabbitMQ and returns the channel.
    """
    await rabbitmq_manager.initialize()
    return rabbitmq_manager.channel


def register_graceful_shutdown(
        channel: AbstractRobustChannel,
        connection: AbstractRobustConnection
) -> None:
    """
    Legacy function - shutdown is now handled by the connection manager.
    This is kept for backward compatibility but does nothing.
    """
    pass  # Shutdown is handled by the singleton manager
