"""
This module contains the RabbitMQ email consumer service for handling email notifications.
It consumes messages from RabbitMQ queues for authentication and order-related emails.
"""

import json
from aio_pika import IncomingMessage, ExchangeType
from aio_pika.abc import AbstractRobustChannel
from app.core.config import config
from app.schemas.email import EmailMessage as EmailLocals
from app.services.rabbitmq.connection import create_rabbitmq_channel
from app.core.logger import logger
from app.services.email_service import EmailService

email_service = EmailService()


async def subscribe_to_auth_email_queue(channel: AbstractRobustChannel | None = None) -> None:
    """
    Consumes authentication email messages from RabbitMQ.
    This function listens for messages on the 'auth-email' queue and processes them.
    It expects messages to contain email details such as template, receiverEmail, and other relevant fields
    :param channel: Optional RabbitMQ channel to use; if None, a new connection will be created.
    """
    try:
        if channel is None:
            channel = await create_rabbitmq_channel()

        exchange_name = "msa-email-notification"
        routing_key = "auth-email"
        queue_name = "auth-email-queue"

        exchange = await channel.declare_exchange(exchange_name, ExchangeType.DIRECT) # type: ignore
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=False) # type: ignore
        await queue.bind(exchange, routing_key)

        async def on_message(message: IncomingMessage):
            async with message.process():
                body = json.loads(message.body.decode())
                logger.info(f"Email message received: {body}")
                locals_ = {
                    "appLink" : config.CLIENT_URL,
                    "appIcon" : "https://res.cloudinary.com/dw3qovmta/image/upload/v1721496044/mui_jkloca.png",
                    "username" : body.get("username"),
                    "verifyLink" : body.get("verifyLink"),
                    "resetLink" : body.get("resetLink")
                }
                await email_service.async_send_email(body["template"], body["receiverEmail"], locals_)

        await queue.consume(on_message) # type: ignore

    except Exception as e:
        logger.error(
            f"NotificationService error in consume_auth_email_messages(): {e}")
