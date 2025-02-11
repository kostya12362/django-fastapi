from contextvars import ContextVar
from typing import Any

from fastapi import Request, Response
from starlette.requests import QueryParams


def params_from_base(query_params: QueryParams) -> dict:
    query_dict: dict[str, Any] = {}
    for key, value in query_params.multi_items():
        if query_dict.get(key):
            query_dict[key] += f",{value}"
        else:
            query_dict[key] = value
    for key, value in query_dict.items():
        if "," in value:
            query_dict[key] = f"[{value}]"
    return query_dict


request_context: ContextVar[Request] = ContextVar("request_context")
response_context: ContextVar[Response] = ContextVar("response_context")


def request() -> Request:
    try:
        return request_context.get()
    except LookupError:
        raise RuntimeError("Request context variable is not set")


def response() -> Response:
    try:
        return response_context.get()
    except LookupError:
        raise RuntimeError("Response context variable is not set")
