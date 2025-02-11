import abc
import json
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from core.schemas import PublicSchema

TDetail = TypeVar("TDetail", bound=PublicSchema)


class BaseMessage(abc.ABC, Generic[TDetail]):
    def __init__(
        self,
        *args: Any,
        message: str,
        status_code: int,
        code: str,
        detail: Optional[TDetail] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        self.message = message.format(*args)
        self.status_code = status_code
        if code.isupper() is False:
            raise ValueError("Code must be uppercase")
        self.code = code
        self.detail = detail
        self.headers = headers


class HTTPException(BaseMessage, Exception):
    def __init__(
        self,
        *args: Any,
        message: str,
        status_code: int,
        code: str,
        detail: Optional[TDetail] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        super().__init__(
            *args,
            message=message,
            status_code=status_code,
            code=code,
            detail=detail,
            headers=headers,
        )


class CustomJSONDecoder(json.JSONDecoder):
    """Custom JSONDecoder for automatic UUID and datetime conversion."""

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self._custom_object_hook, *args, **kwargs)

    def _custom_object_hook(self, obj):
        """Automatically converts UUID and datetime if possible."""
        for key, value in obj.items():
            if isinstance(value, str):
                # Trying to convert to UUID
                try:
                    obj[key] = UUID(value)
                    continue
                except ValueError:
                    pass

                # Trying to convert to datetime
                try:
                    obj[key] = datetime.fromisoformat(value)
                    continue
                except ValueError:
                    pass

        return obj
