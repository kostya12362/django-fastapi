from typing import Any, TypeVar

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T", bound=Any)


def QueryField(default: T, *args: Any, **kwargs: Any):  # noqa
    return Field(default_factory=Query(*args, default_factory=default, **kwargs))


class QueryFiter(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
