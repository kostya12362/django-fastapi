from collections.abc import Mapping
from enum import Enum
from typing import Annotated, Any, Generic, Optional

from pydantic import Field, conlist

from core.schemas.base import PublicSchema, _PublicSchema

__all__ = (
    "ResponseMulti",
    "Response",
    "MessageResponse",
    "ErrorResponse",
    "EventResponse",
    "ErrorResponseMulti",
    "_Response",
)


class ResponseMulti(PublicSchema, Generic[_PublicSchema]):
    """Generic response schema that consist multiple results."""

    data: list[_PublicSchema]


class Response(PublicSchema, Generic[_PublicSchema]):
    """Generic response schema that consist only one result."""

    data: _PublicSchema


class StatusEnum(str, Enum):
    success = "success"
    error = "error"


class TypeResponse(str, Enum):
    message = "message"
    error = "error"
    event = "event"


class MessageResponse(PublicSchema, Generic[_PublicSchema]):
    """Generic response schema that consist only one result."""

    message: str = Field(description="This field represent the message")
    code: str = Field(description="Message code")
    status: Optional[StatusEnum] = Field(
        description="Message status", default=StatusEnum.success
    )
    type: Optional[TypeResponse] = Field(
        description="Type response", default=TypeResponse.message
    )
    detail: Optional[_PublicSchema] = Field(None, description="The message detail")


class ErrorResponse(MessageResponse):
    """Error response schema."""

    status: Optional[StatusEnum] = Field(
        description="Message status", default=StatusEnum.error
    )
    code: str = Field(description="The error code")
    type: Optional[TypeResponse] = Field(
        description="Type response", default=TypeResponse.error
    )
    detail: Optional[PublicSchema] = Field(None, description="The error detail")
    path: list[int | str] = Field(
        description="The path to the field that raised the error",
        default_factory=list,
    )


class EventResponse(MessageResponse):
    """Event response schema."""

    id: str = Field(description="The event id")
    status: Optional[StatusEnum] = Field(
        description="Message status", default=StatusEnum.success
    )
    code: str = Field(description="The event code")
    type: Optional[TypeResponse] = Field(
        description="Type response", default=TypeResponse.event
    )


class ErrorResponseMulti(PublicSchema):
    """The public error response schema that includes multiple objects."""

    errors: Annotated[list[ErrorResponse], conlist(ErrorResponse, min_length=1)]


_Response = Mapping[int | str, dict[str, Any]]
