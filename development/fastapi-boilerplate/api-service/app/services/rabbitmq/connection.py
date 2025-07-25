import asyncio
import signal
from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustChannel, AbstractRobustConnection
from aio_pika.exceptions import AMQPConnectionError

from app.core.config import config
from app.core.logger import logger
from app.core.constants import SERVICE_NAME

async def create_rabbitmq_channel() -> AbstractRobustChannel | None:
    """
    Establishes a connection to RabbitMQ and returns the channel.
    :return: The created channel or None if connection fails.
    """
    if not config.RABBITMQ_ENDPOINT:
        logger.error("RabbitMQ endpoint is not configured.")
        return None

    try:
        connection: AbstractRobustConnection = await connect_robust(config.RABBITMQ_ENDPOINT)
        channel: AbstractRobustChannel = await connection.channel()  # type: ignore
        # Register signal handler to close connection on SIGINT
        register_graceful_shutdown(channel, connection)

        return channel
    except AMQPConnectionError as error:
        logger.error(f"Failed to connect to RabbitMQ: {error}")
    except Exception as error:
        logger.error(f"Unexpected error in create_rabbitmq_channel(): {error}")

    return None

def register_graceful_shutdown(channel: AbstractRobustChannel, connection: AbstractRobustConnection) -> None:
    """
    Closes the RabbitMQ channel and connection on SIGINT (Ctrl+C).
    """
    async def close_connection() -> None:
        try:
            await channel.close()
            await connection.close()
            logger.info("RabbitMQ channel and connection closed gracefully.")
        except Exception as error:
            logger.error(f"Error during RabbitMQ shutdown: {error}")

    def handler(signum, frame) -> None:
        logger.info("Received SIGINT, shutting down...")
        asyncio.create_task(close_connection())

    signal.signal(signal.SIGINT, handler)
