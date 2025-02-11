import inspect
import json
from functools import wraps
from typing import Callable

from aio_pika import IncomingMessage
from loguru import logger

from core.schemas.utils import CustomJSONDecoder


class BrokerRegistry:
    def __init__(self):
        self.map_rpc_callbacks: dict[str, Callable] = {}
        self.map_consumers: dict[str, tuple[Callable, int]] = {}

    def rpc(self, method_name: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            if not inspect.iscoroutinefunction(func):
                raise ValueError("RPC function must be a coroutine function")

            if method_name in self.map_rpc_callbacks:
                raise ValueError(f"RPC method '{method_name}' have already declared. 1")
            self.map_rpc_callbacks[method_name] = func
            return func

        return decorator

    def consumer(self, queue_name: str, num_consumers: int = 1):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(message: IncomingMessage):
                if not inspect.iscoroutinefunction(func):
                    raise ValueError("Consumer function must be a coroutine function")
                try:
                    # Decode message body from JSON into dictionary
                    payload = json.loads(
                        message.body.decode("utf-8"), cls=CustomJSONDecoder
                    )
                    # Pass the unpacked dictionary as named arguments to the function
                    await func(**payload)
                except json.JSONDecodeError:
                    logger.error("JSON decoding error")
                except TypeError as e:
                    logger.error(f"Error passing arguments to function: {e}")
                finally:
                    await message.ack()

            if queue_name in self.map_consumers:
                raise ValueError(
                    f"Consumer for the queue '{queue_name}' already registered."
                )
            self.map_consumers[queue_name] = (
                wrapper,
                num_consumers,
            )
            return wrapper

        return decorator
