"""
This module contains the RabbitMQ email consumer service for handling email notifications.
It consumes messages from RabbitMQ queues for authentication and order-related emails.
"""

import json
from aio_pika import IncomingMessage, ExchangeType
from aio_pika.abc import AbstractRobustChannel
from app.services.rabbitmq.connection import create_rabbitmq_channel
from app.core.logger import logger
from app.services.catalog_service import CatalogService



async def consume_catalog_direct_message(channel: AbstractRobustChannel | None = None) -> None:
    """
    Consume messages from 'msa-update-catalog' exchange and update catalog reviews.
    """
    try:
        if channel is None:
            channel = await create_rabbitmq_channel()

        exchange_name = "msa-update-catalog"
        routing_key = "update-catalog"
        queue_name = "catalog-update-queue"

        exchange = await channel.declare_exchange(exchange_name, ExchangeType.DIRECT, durable=True)  # type: ignore
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=False)  # type: ignore
        await queue.bind(exchange, routing_key)

        async def on_message(message: IncomingMessage):
            async with message.process():
                try:
                    payload = json.loads(message.body.decode())
                    logger.info(f"catalog update message received: {payload}")

                    catalog_review = payload.get("catalog_review")
                    if catalog_review:
                        await CatalogService.update_category_review(catalog_review["catalog_id"], catalog_review["rating"])
                except Exception as e:
                    logger.error(f"Error processing catalog update message: {e}, body={message.body.decode()}")

        await queue.consume(on_message)  # type: ignore

    except Exception as e:
        logger.error(f"consume_catalog_direct_message() error: {e}")


