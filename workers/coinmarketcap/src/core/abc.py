from abc import ABC, abstractmethod
from typing import Any

# ===== Abstract classes (interfaces) for pipeline components =====


class AbstractBlockFetcher(ABC):
    @abstractmethod
    async def fetch(self, *args: Any, **kwargs: Any) -> dict:
        """Get block data from an external API."""
        pass


class AbstractQueuePublisher(ABC):
    @abstractmethod
    async def publish(self, block_data: dict[str, Any]) -> None:
        """Publish block data to the message queue."""
        pass


class BaseWorker(ABC):
    @abstractmethod
    async def start(self) -> None:
        pass

    @classmethod
    @abstractmethod
    async def init(cls):
        pass
