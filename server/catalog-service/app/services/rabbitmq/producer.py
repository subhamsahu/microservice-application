"""
This module contains the RabbitMQ email consumer service for handling email notifications.
It consumes messages from RabbitMQ queues for authentication and order-related emails.
"""

import json
from aio_pika import ExchangeType
from aio_pika.abc import AbstractRobustChannel
from aio_pika import Message

from app.core.config import config
from app.services.rabbitmq.connection import create_rabbitmq_channel
from app.core.logger import logger

# Old: publish_test_email
class FailedToPublishRabbitMQMessage(Exception):
    """
    Exception raised when publishing a message to RabbitMQ fails.
    """

async def publish_message_to_queue(
        channel: AbstractRobustChannel,
        exchange_name: str,
        routing_key: str,
        message: dict,
        exchange_type: ExchangeType = ExchangeType.DIRECT,
):
    """
    Function to publish a message to RabbitMQ.
    """
    try:
        if not channel:
            channel = await create_rabbitmq_channel()

        exchange = await channel.declare_exchange(exchange_name, exchange_type)

        message_body = Message(
            body=json.dumps(message).encode(),
            content_type="application/json"
        )

        await exchange.publish(message_body, routing_key=routing_key)
        logger.info("Published message to exchange.")
    except FailedToPublishRabbitMQMessage as exc:
        logger.error(f"Failed to publish message to RabbitMQ: {exc}")
