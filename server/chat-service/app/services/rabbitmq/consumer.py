"""
This module contains the RabbitMQ chat consumer service for handling chat messages.
It consumes messages from RabbitMQ queues for chat-related events.
"""

import json
from aio_pika import IncomingMessage, ExchangeType
from aio_pika.abc import AbstractRobustChannel
from app.services.rabbitmq.connection import create_rabbitmq_channel
from app.core.logger import logger
from app.services.chat_service import ChatService



async def consume_chat_direct_message(channel: AbstractRobustChannel | None = None) -> None:
    """
    Consume messages from 'msa-chat-notifications' exchange and handle chat events.
    """
    try:
        if channel is None:
            channel = await create_rabbitmq_channel()

        exchange_name = "msa-chat-notifications"
        routing_key = "chat-notification"
        queue_name = "chat-notification-queue"

        exchange = await channel.declare_exchange(exchange_name, ExchangeType.DIRECT, durable=True)  # type: ignore
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=False)  # type: ignore
        await queue.bind(exchange, routing_key)

        async def on_message(message: IncomingMessage):
            async with message.process():
                try:
                    payload = json.loads(message.body.decode())
                    logger.info(f"chat notification message received: {payload}")

                    message_data = payload.get("message_data")
                    if message_data:
                        await ChatService.handle_notification(message_data)
                except Exception as e:
                    logger.error(f"Error processing chat notification message: {e}, body={message.body.decode()}")

        await queue.consume(on_message)  # type: ignore

    except Exception as e:
        logger.error(f"consume_chat_direct_message() error: {e}")