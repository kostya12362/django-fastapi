import asyncio
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from blockchains.api.routers import router as blockchains_router
from blockchains.registry import registry
from core.broker import setup_broker
from users.api.routers import router as users_router

__all__ = (
    "routers",
    "lifespan",
)

routers: list[APIRouter] = [
    users_router,
    blockchains_router,
]


@asynccontextmanager
async def lifespan(application: FastAPI):
    loop = asyncio.get_event_loop()
    task = asyncio.create_task(
        setup_broker(app=application, registries=[registry], loop=loop)
    )
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
