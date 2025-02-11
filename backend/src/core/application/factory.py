from typing import Iterable, Optional

from django.conf import settings
from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import Mount
from pydantic import ValidationError
from starlette.types import Lifespan

from core.errors import (
    MAP_ERROR_HANDLERS,
    HTTPException,
    custom_base_errors_handler,
    python_base_error_handler,
    request_validation_errors_handler,
    response_validation_errors_handler,
)
from core.middlewares import (
    QueryStringFlatteningMiddleware,
    RequestResponseContextMiddleware,
    ResponseTimeMiddleware,
)

from .openapi import custom_openapi

__all__ = ("create",)


def create(
    *_,
    rest_routers: Iterable[APIRouter],
    mount_routers: Iterable[Mount],
    lifespan: Optional[Lifespan[FastAPI]] = None,
    **kwargs,
) -> FastAPI | None:
    """The application factory using FastAPI framework.
    🎉 Only passing routes is mandatory to start.
    """
    app = FastAPI(
        title=settings.PUBLIC_API.name,
        lifespan=lifespan,
        docs_url=settings.PUBLIC_API.urls.docs,
        redoc_url=settings.PUBLIC_API.urls.re_doc,
        exception_handlers=MAP_ERROR_HANDLERS,
        **kwargs,
    )

    # ========= Error Handlers =========
    # Extend FastAPI default error handlers

    app.exception_handler(RequestValidationError)(request_validation_errors_handler)
    app.exception_handler(ResponseValidationError)(response_validation_errors_handler)
    app.exception_handler(HTTPException)(custom_base_errors_handler)
    app.exception_handler(ValidationError)(response_validation_errors_handler)
    if settings.DEBUG is False:
        app.exception_handler(Exception)(python_base_error_handler)

    # Include REST API routers
    for router in rest_routers:
        app.include_router(router)

    for mount in mount_routers:
        app.mount(path=mount.path, app=mount.app, name=mount.name)
    # ========= Middleware =========
    # Setup middlewares
    app.add_middleware(
        CORSMiddleware,  # noqa
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(ResponseTimeMiddleware)  # noqa
    app.add_middleware(QueryStringFlatteningMiddleware)  # noqa
    app.add_middleware(RequestResponseContextMiddleware)  # noqa

    custom_openapi(app)

    return app
