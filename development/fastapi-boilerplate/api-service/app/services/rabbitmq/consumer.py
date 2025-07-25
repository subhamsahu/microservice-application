"""
This module contains the RabbitMQ email consumer service for handling email notifications.
It consumes messages from RabbitMQ queues for authentication and order-related emails.
"""

import json
from aio_pika import IncomingMessage, ExchangeType
from aio_pika.abc import AbstractRobustChannel

from app.core.config import config
from app.services.rabbitmq.connection import create_rabbitmq_channel
from app.core.logger import logger

# Old: publish_test_email

async def publish_message():
    """
    Test function to publish a message to RabbitMQ.
    """
    from aio_pika import Message
    channel = await create_rabbitmq_channel()
    if not channel:
        logger.error("RabbitMQ channel not available for publishing.")
        return

    exchange = await channel.declare_exchange("msa-test-exchange", ExchangeType.DIRECT)

    message_body = {
        "event": "created-user",
        "details": {
            "username": "testuser",
            "email": "test@email.com"
        }
    }

    message = Message(
        body=json.dumps(message_body).encode(),
        content_type="application/json"
    )

    await exchange.publish(message, routing_key="test-route")
    logger.info("Published email message to exchange.")


async def subscribe_to_queue(channel: AbstractRobustChannel | None = None) -> None:
    """
    Consumes messages from RabbitMQ.
    """
    try:
        if channel is None:
            channel = await create_rabbitmq_channel()

        exchange_name = "msa-test-exchange"
        routing_key = "test-route"
        queue_name = "test-queue"

        exchange = await channel.declare_exchange(exchange_name, ExchangeType.DIRECT) # type: ignore
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=False) # type: ignore
        await queue.bind(exchange, routing_key)

        async def on_message(message: IncomingMessage):
            async with message.process():
                body = json.loads(message.body.decode())
                logger.info(f"Message received: {body}")
        await queue.consume(on_message) # type: ignore

    except Exception as e:
        logger.error(
            f"NotificationService error in consume_auth_email_messages(): {e}")
