"""
This module contains the RabbitMQ email consumer service for handling email notifications.
It consumes messages from RabbitMQ queues for authentication and order-related emails.
"""

import json
from aio_pika import IncomingMessage, ExchangeType
from aio_pika.abc import AbstractRobustChannel
from app.services.rabbitmq.connection import create_rabbitmq_channel
from app.core.logger import logger
from app.services.buyer_service import BuyerService


async def subscribe_to_buyer_update_queue(channel: AbstractRobustChannel | None = None) -> None:
    """
    Subscribe to the buyer creation queue and process incoming messages.
    """
    try:
        if channel is None:
            channel = await create_rabbitmq_channel()

        exchange_name = "msa-buyer-update"
        routing_key = "user-buyer"
        queue_name = "user-buyer-queue"

        exchange = await channel.declare_exchange(exchange_name, ExchangeType.DIRECT) # type: ignore
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=False) # type: ignore
        await queue.bind(exchange, routing_key)

        async def on_message(message: IncomingMessage):
            async with message.process():
                body = json.loads(message.body.decode())
                logger.info(f"Buyer data received: {body}")
                from_service = body.get("from")
                if from_service == "auth_service":
                    await BuyerService.create_buyer_from_auth(body.get("user_data"))
                elif from_service == "order_service":
                    await BuyerService.update_buyer(body.get("buyer_id"), body.get("buyer_data"))
                else:
                    logger.warning(f"Unknown service '{from_service}' in message: {body}")
        await queue.consume(on_message) # type: ignore

    except Exception as e:
        logger.error(
            f"NotificationService error in subscribe_to_buyer_create_queue(): {e}")
