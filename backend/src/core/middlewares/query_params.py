from typing import Any, Callable
from urllib.parse import urlencode

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import QueryParams

from core.utils import params_from_base


class QueryStringFlatteningMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request.scope["query_string"] = self.params_to_base(request.query_params)
        response = await call_next(request)
        new_query_params: dict = params_from_base(request.query_params)
        request.url.replace_query_params(**new_query_params)
        return response

    @staticmethod
    def params_to_base(query_params: QueryParams) -> bytes:
        flattened: list[tuple[str, Any]] = []
        for key, value in query_params.multi_items():
            flattened.extend((key, entry) for entry in value.split(","))
        return urlencode(flattened, doseq=True).encode("utf-8")
