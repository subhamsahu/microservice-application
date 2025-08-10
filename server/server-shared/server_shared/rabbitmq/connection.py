"""
Module for rabbitmq connection
"""
import asyncio
import logging
from typing import Optional
from aio_pika import connect_robust, Message, ExchangeType, AbstractRobustConnection, AbstractRobustChannel, RobustQueue
from aio_pika.exceptions import AMQPConnectionError

logger = logging.getLogger(__name__)

class RabbitMQManager:
    _connection: Optional[AbstractRobustConnection] = None
    _channel: Optional[AbstractRobustChannel] = None
    _lock: asyncio.Lock

    def __init__(self, endpoint: str, exchange_name: str = "default_exchange", queue_name: str = "default_queue", routing_key: str = "default_key"):
        self._endpoint = endpoint
        self._exchange_name = exchange_name
        self._queue_name = queue_name
        self._routing_key = routing_key
        self._lock = asyncio.Lock()
        self._exchange = None
        self._queue: Optional[RobustQueue] = None

    async def get_channel(self) -> Optional[AbstractRobustChannel]:
        """
        Returns an existing channel or creates a new one if needed.
        Automatically reconnects if the connection is lost.
        """
        async with self._lock:
            if self._channel and not self._channel.is_closed:
                return self._channel

            await self._connect()
            return self._channel

    async def _connect(self):
        """
        Establishes a robust connection with auto-retry and auto-declares exchange & queue.
        """
        retries = 0
        while True:
            try:
                logger.info(f"Connecting to RabbitMQ at {self._endpoint} (attempt {retries + 1})...")
                self._connection = await connect_robust(self._endpoint)
                self._channel = await self._connection.channel()
                await self._setup_topology()
                logger.info("RabbitMQ connection established and topology declared.")
                return
            except AMQPConnectionError as error:
                retries += 1
                wait_time = min(5 * retries, 30)  # Exponential backoff
                logger.error(f"RabbitMQ connection failed: {error}. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            except Exception as error:
                logger.exception(f"Unexpected error during RabbitMQ connection: {error}")
                await asyncio.sleep(10)

    async def _setup_topology(self):
        """
        Declares exchange, queue, and bindings.
        """
        self._exchange = await self._channel.declare_exchange(
            self._exchange_name, ExchangeType.DIRECT, durable=True
        )
        self._queue = await self._channel.declare_queue(
            self._queue_name, durable=True
        )
        await self._queue.bind(self._exchange, routing_key=self._routing_key)

    async def publish(self, message_body: str):
        """
        Publishes a message to the declared exchange & queue.
        """
        channel = await self.get_channel()
        if channel:
            await self._exchange.publish(
                Message(body=message_body.encode()),
                routing_key=self._routing_key
            )
            logger.info(f"Message published to {self._queue_name}: {message_body}")
        else:
            logger.error("Cannot publish message — RabbitMQ unavailable.")

    async def close(self):
        """
        Closes the RabbitMQ connection and channel gracefully.
        """
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
        logger.info("RabbitMQ connection closed.")
