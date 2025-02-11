from asyncio import AbstractEventLoop, create_task
from dataclasses import dataclass
from typing import Awaitable, Callable, Iterable

from aio_pika import Channel, Connection, connect_robust
from aio_pika.abc import AbstractIncomingMessage, AbstractQueue
from aio_pika.patterns import RPC
from django.conf import settings
from fastapi import FastAPI, Request
from loguru import logger

from core.broker.tools import BrokerRegistry

__all__ = (
    "BrokerRegistry",
    "setup_broker",
)


@dataclass
class BrokerData:
    connection: Connection
    channel: Channel
    rpc: RPC


async def setup_broker(
    app: FastAPI, registries: Iterable[BrokerRegistry], loop: AbstractEventLoop
) -> None:
    # Establish connection
    connection = await connect_robust(settings.BROKER.uri, loop=loop)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    # Initialize RPC
    rpc = await RPC.create(channel)
    for broker_registry in registries:
        for method_name, callback in broker_registry.map_rpc_callbacks.items():
            await rpc.register(method_name, callback, auto_delete=True)
            logger.info(
                f"Registered | {callback.__module__}{callback.__name__} |  RPC callback"  # noqa
            )  # noqa
        for queue_name, (
            handler,
            num_consumers,
        ) in broker_registry.map_consumers.items():
            queue = await channel.declare_queue(
                queue_name, auto_delete=False, durable=True
            )
            for i in range(num_consumers):
                logger.info(
                    f"Consumer | {callback.__module__}{callback.__name__} | "  # noqa
                    f"{i} | started consuming messages from queue '{queue_name}'"
                )

                create_task(consume_messages(queue, handler))  # noqa
            logger.info(f"Registered consumer for queue: '{queue_name}'")

    # Store in app.state using BrokerData
    app.state.broker = BrokerData(  # noqa
        connection=connection,  # type: ignore
        channel=channel,  # type: ignore
        rpc=rpc,
    )

    logger.info("Broker setup completed.")


async def consume_messages(
    queue: AbstractQueue,
    handler: Callable[[AbstractIncomingMessage], Awaitable[None]],
) -> None:
    """Constantly listening to the queue and processing messages"""
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process(ignore_processed=True):  # noqa
                await handler(message)  # noqa


async def get_broker(request: Request) -> BrokerData:
    return request.app.state.broker
