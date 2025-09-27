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
from app.services.seller_service import SellerService
from app.services.rabbitmq.producer import publish_message_to_queue


async def consume_buyer_update_direct_message(channel: AbstractRobustChannel | None = None) -> None:
    """
    Subscribe to the buyer creation queue and process incoming messages.
    """
    try:
        if channel is None:
            channel = await create_rabbitmq_channel()

        exchange_name = "msa-buyer-update"
        routing_key = "user-buyer"
        queue_name = "user-buyer-queue"

        # type: ignore
        exchange = await channel.declare_exchange(exchange_name, ExchangeType.DIRECT)
        # type: ignore
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=False)
        await queue.bind(exchange, routing_key)

        async def on_message(message: IncomingMessage):
            async with message.process():
                try:
                    body = json.loads(message.body.decode())
                    logger.info(f"Buyer data received: {body}")
                    from_service = body.get("from")
                    if from_service == "auth_service":
                        await BuyerService.create_buyer_from_auth(body.get("user_data"))
                    elif from_service == "order_service":
                        await BuyerService.update_buyer(body.get("buyer_id"), body.get("buyer_data"))
                    else:
                        logger.warning(
                            f"Unknown service '{from_service}' in message: {body}")
                except Exception as e:
                    logger.error(f"Error processing seller message: {e}")
        await queue.consume(on_message)  # type: ignore

    except Exception as e:
        logger.error(
            f"NotificationService error in subscribe_to_buyer_create_queue(): {e}")


async def consume_seller_update_direct_message(channel: AbstractRobustChannel | None = None) -> None:
    """
    Queue Implementation to consume seller update info from other services
    """
    try:
        if channel is None:
            channel = await create_rabbitmq_channel()

        exchange_name = "msa-seller-update"
        routing_key = "user-seller"
        queue_name = "user-seller-queue"

        exchange = await channel.declare_exchange(exchange_name, ExchangeType.DIRECT) # type: ignore
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=False) # type: ignore
        await queue.bind(exchange, routing_key)

        async def on_message(message: IncomingMessage):
            async with message.process():
                try:
                    payload = json.loads(message.body.decode())
                    logger.info(f"Seller message received: {payload}")
                    from_service = payload.get("from")
                    if from_service != "catalog_service":
                        raise Exception("Recieved Event from Unknown Service")
                    event = payload.get("event")
                    logger.info(f"{event=}")
                    if event == "create-order":
                        await SellerService.update_seller(payload["seller_id"], payload["update-data"])
                    elif event == "approve-order":
                        await SellerService.update_seller(payload["seller_id"], payload["update-data"])
                    elif event == "update-catalog-count":
                        logger.info(f"{payload["update_data"]=}")
                        await SellerService.update_total_catalogs(payload["update_data"]["seller_id"], payload["update_data"]["count"])
                    elif event == "cancel-order":
                        await SellerService.update_seller(payload["seller_id"], payload["update-data"])
                except Exception as e:
                    import traceback
                    logger.error(
                        f"Error processing seller message: {e} {traceback.format_exc()}")

        await queue.consume(on_message)  # type: ignore

    except Exception as e:
        logger.error(f"consume_seller_direct_message() error: {e}")


async def consume_review_fanout_messages(channel: AbstractRobustChannel | None = None) -> None:
    """Fanout Queue Implementation to consume review message coming from other services"""
    try:
        if channel is None:
            channel = await create_rabbitmq_channel()

        exchange_name = "msa-review"
        queue_name = "seller-review-queue"

        exchange = await channel.declare_exchange(exchange_name, ExchangeType.FANOUT) # type: ignore
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=False) # type: ignore
        await queue.bind(exchange)

        async def on_message(message: IncomingMessage):
            async with message.process():
                try:
                    payload = json.loads(message.body.decode())
                    logger.info(f"Review message received: {payload}")

                    if payload.get("type") == "buyer-review":
                        await SellerService.update_seller(payload["seller_id"], payload["update-data"])

                        # publish message to catalog service
                        await publish_message_to_queue(
                            channel,
                            exchange_name="msa-update-catalog",
                            routing_key="",
                            message={"type": "update-catalog", "catalog-review": payload},
                            exchange_type=ExchangeType.FANOUT
                        )
                except Exception as e:
                    logger.error(
                        f"Error processing review message: {e}, body={message.body.decode()}")

        await queue.consume(on_message)  # type: ignore

    except Exception as e:
        logger.error(f"consume_review_fanout_messages() error: {e}")


async def consume_seed_catalog_direct_messages(channel: AbstractRobustChannel | None = None) -> None:
    try:
        if channel is None:
            channel = await create_rabbitmq_channel()

        exchange_name = "msa-catalog"
        routing_key = "get-sellers"
        queue_name = "user-catalog-queue"

        # type: ignore
        exchange = await channel.declare_exchange(exchange_name, ExchangeType.DIRECT)
        # type: ignore
        queue = await channel.declare_queue(queue_name, durable=True, auto_delete=False)
        await queue.bind(exchange, routing_key)

        async def on_message(message: IncomingMessage):
            async with message.process():
                try:
                    payload = json.loads(message.body.decode())
                    logger.info(f"Seed catalog message received: {payload}")

                    if payload.get("type") == "getSellers":
                        sellers = await get_random_sellers(int(payload["count"]))
                        await publish_direct_message(
                            channel,
                            "msa-seed-catalog",
                            "receive-sellers",
                            json.dumps(
                                {"type": "receiveSellers", "sellers": sellers, "count": payload["count"]}),
                            "Message sent to catalog service.",
                        )
                except Exception as e:
                    logger.error(
                        f"Error processing seed catalog message: {e}, body={message.body.decode()}")

        await queue.consume(on_message)  # type: ignore

    except Exception as e:
        logger.error(f"consume_seed_catalog_direct_messages() error: {e}")
