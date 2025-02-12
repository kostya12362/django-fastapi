import asyncio
import json
import os
from datetime import datetime, timezone

import httpx
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractChannel, AbstractQueue
from aio_pika.patterns import RPC
from loguru import logger

from core.abc import AbstractBlockFetcher, AbstractQueuePublisher, BaseWorker

BROKER_URI = os.environ["BROKER_URI"]  # "amqp://admin:admin@localhost/"
QUEUE_NAME = "blockchains:save_block"
TIMEOUT = int(os.getenv("TIMEOUT", 60))  # 5
PROXY = os.getenv("PROXY") or None

# ===== Specific implementations =====


class BlockchairBlockFetcher(AbstractBlockFetcher):
    API_URL = "https://api.blockchair.com/ethereum/stats"

    @staticmethod
    def parse_utc_datetime(utc_time_str: str) -> datetime:
        """Parses a UTC string and returns a UTC aware datetime object."""
        naive_datetime = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")
        return naive_datetime.astimezone(tz=timezone.utc)

    async def fetch(self) -> dict:
        async with httpx.AsyncClient(proxy=PROXY, verify=False, timeout=50) as client:
            response = await client.get(self.API_URL)
            response.raise_for_status()
            data = response.json()["data"]
            block_data = {
                "block_number": data["blocks"],
                "created_at": self.parse_utc_datetime(
                    data["best_block_time"]
                ).isoformat(),
            }
            return block_data

    # async def get_api_key(self):


class RabbitMQPublisher(AbstractQueuePublisher):
    def __init__(self, channel: AbstractChannel, queue_name: str):
        self.channel = channel
        self.queue_name = queue_name

    async def publish(self, data: dict) -> None:
        message = Message(
            body=json.dumps(data).encode(),
            # the message is saved to disk and will survive broker restarts
            delivery_mode=2,
        )
        await self.channel.default_exchange.publish(
            message, routing_key=self.queue_name
        )


# ===== The main Worker that unites all components =====


class BlockWorker(BaseWorker):
    provider_name: str = "blockchair"
    currency_name: str = "ETH"

    def __init__(
            self, rpc: RPC, channel: AbstractChannel, queue: AbstractQueue
    ):
        self.rpc = rpc
        self.channel = channel
        self.queue = queue

        # Components pipeline
        self.fetcher: AbstractBlockFetcher = BlockchairBlockFetcher()
        self.publisher: AbstractQueuePublisher = RabbitMQPublisher(
            channel, QUEUE_NAME
        )
        self._last_block_number: int = 0

    async def start(self) -> None:
        provider_id, currency_id = await asyncio.gather(
            self.rpc.proxy.save_provider(name=self.provider_name),
            self.rpc.proxy.save_currency(name=self.currency_name),
        )
        logger.info(f"Provider ID: {provider_id}, Currency ID: {currency_id}")
        while True:
            try:
                block_data = await self.fetcher.fetch()
                current_block_number = block_data.get("block_number")
                # Enriching data with currency and provider information via RPC
                block_data.update(
                    {
                        "provider_id": provider_id,
                        "currency_id": currency_id,
                    }
                )
                if current_block_number != self._last_block_number:
                    logger.info(f"Publishing block data: {block_data}")
                    await self.publisher.publish(block_data)
                    self._last_block_number = current_block_number
            except Exception as e:
                logger.error(f"Error occurred: {e}")
            await asyncio.sleep(TIMEOUT)  # Pause between requests

    @classmethod
    async def init(cls) -> "BlockWorker":
        connection = await connect_robust(BROKER_URI)
        channel = await connection.channel()
        rpc = await RPC.create(channel)
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        worker = cls(rpc=rpc, channel=channel, queue=queue)
        return worker


# ===== Entry point =====


async def main():
    worker = await BlockWorker.init()
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
