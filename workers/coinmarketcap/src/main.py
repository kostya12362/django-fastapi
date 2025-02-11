import asyncio
import json
import os
from datetime import datetime

import httpx
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractChannel, AbstractQueue
from aio_pika.patterns import RPC
from loguru import logger

from core.abc import AbstractBlockFetcher, AbstractQueuePublisher, BaseWorker

BROKER_URI = os.environ["BROKER_URI"]  # "amqp://admin:admin@localhost/"
QUEUE_NAME = "blockchains:save_block"
TIMEOUT = int(os.getenv("TIMEOUT", 60))  # 5
PROXY = os.getenv("PROXY")


# ===== Specific implementations =====


class CoinMarketCapBlockFetcher(AbstractBlockFetcher):
    API_URL = (
        "https://pro-api.coinmarketcap.com/v1/blockchain/statistics/latest"
    )

    async def fetch(self, headers: dict[str, str]) -> dict:
        async with httpx.AsyncClient(proxy=PROXY, headers=headers) as client:
            response = await client.get(self.API_URL)
            response.raise_for_status()
            data = response.json()["data"]["BTC"]
            block_data = {
                "block_number": data["total_blocks"],
                "created_at": datetime.now().isoformat(),
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
    provider_name: str = "coinmarketcap"
    currency_name: str = "BTC"

    def __init__(
        self, rpc: RPC, channel: AbstractChannel, queue: AbstractQueue
    ):
        self.rpc = rpc
        self.channel = channel
        self.queue = queue

        # Components pipeline
        self.fetcher: AbstractBlockFetcher = CoinMarketCapBlockFetcher()
        self.publisher: AbstractQueuePublisher = RabbitMQPublisher(
            channel, QUEUE_NAME
        )
        self._last_block_number: int = 0
        self._last_api_key: str = ""

    async def get_api_key(self, provider_id: int) -> str:
        """Gets the provider's API key. Uses cache in case of error."""
        try:
            provider = await self.rpc.proxy.get_provider(
                provider_id=provider_id
            )
            api_key = provider.get("api_key")
            if api_key:
                self._last_api_key = api_key
            return self._last_api_key
        except Exception as e:
            logger.warning(f"Failed to get API key: {e}")
            return (
                self._last_api_key
            )  # Возвращает старый ключ, если новый не получен

    async def process_block(self, provider_id: int, currency_id: int) -> None:
        """Handles block retrieval and publishing."""
        api_key = await self.get_api_key(provider_id)

        if not api_key:
            logger.error("API key missing! Skipping iteration...")
            return

        block_data = await self.fetcher.fetch(
            headers={"X-CMC_PRO_API_KEY": api_key}
        )
        current_block_number = block_data["block_number"]

        # Check for duplicate block
        if current_block_number == self._last_block_number:
            logger.debug(
                "The block has already been processed, let's skip it."
            )
            return

        block_data.update(
            {"provider_id": provider_id, "currency_id": currency_id}
        )
        logger.info(f"Publishing a block: {block_data}")
        await self.publisher.publish(block_data)

        self._last_block_number = current_block_number

    async def start(self) -> None:
        """Basic block processing cycle."""
        provider_id, currency_id = await asyncio.gather(
            self.rpc.proxy.save_provider(name=self.provider_name),
            self.rpc.proxy.save_currency(name=self.currency_name),
        )
        logger.info(
            f"Worker started | Provider ID:"
            f" {provider_id}, Currency ID: {currency_id}"
        )

        while True:
            try:
                await self.process_block(provider_id, currency_id)
            except Exception as e:
                logger.error(f"Block processing error: {e}")

            await asyncio.sleep(TIMEOUT)

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
