import os
from typing import Any, Awaitable, Callable, MutableMapping, cast

from django.conf import settings
from django.core.asgi import get_asgi_application
from fastapi.routing import Mount
from fastapi.staticfiles import StaticFiles

from core.application import factory, setup_logger

ASGIApp = Callable[  # noqa
    [
        MutableMapping[str, Any],
        Callable[[], Awaitable[MutableMapping[str, Any]]],
        Callable[[MutableMapping[str, Any]], Awaitable[None]],
    ],
    Awaitable[None],
]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

setup_logger(
    log_format=settings.LOGGING_FORMAT,
)

application = get_asgi_application()
django_app: ASGIApp = cast(ASGIApp, application)

from server.api import lifespan, routers  # noqa

app = factory.create(
    lifespan=lifespan,
    rest_routers=routers,
    mount_routers=[
        Mount(
            "/static/",
            StaticFiles(directory=settings.STATIC_ROOT),
            name="static",
        ),
        Mount("/", django_app, name="django"),
    ],
    debug=settings.DEBUG,
)
