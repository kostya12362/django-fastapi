from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from core.utils import request_context, response_context


class RequestResponseContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        request_context.set(request)
        response = await call_next(request)
        response_context.set(response)
        return response
