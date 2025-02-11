"""
This schema includes basic data schemas that are used in the whole application.
"""
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, model_serializer

__all__ = (
    "InternalSchema",
    "_InternalSchema",
    "PublicSchema",
    "_PublicSchema",
    "FrozenSchema",
)


def to_camelcase(string: str) -> str:
    """The alias generator for PublicSchema."""

    resp = "".join(
        word.capitalize() if index else word
        for index, word in enumerate(string.split("_"))
    )
    return resp


class FrozenSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )


class InternalSchema(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
    )


class PublicSchema(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        extra="forbid",
    )

    @classmethod
    def reorder_data(cls, data: Any) -> Any:
        """Reorder the data to have a better serialization"""
        normal: list[tuple[Any, Any]] = []
        dct: list[tuple[Any, Any]] = []
        lst: list[tuple[Any, Any]] = []

        if isinstance(data, dict):
            for k, v in data.items():
                v = cls.reorder_data(v)
                (
                    dct
                    if isinstance(v, dict)
                    else lst
                    if isinstance(v, list)
                    else normal
                ).append((k, v))
            return {k: v for k, v in normal + dct + lst}
        elif isinstance(data, list):
            for x in data:
                x = cls.reorder_data(x)
                (
                    dct
                    if isinstance(x, dict)
                    else lst
                    if isinstance(x, list)
                    else normal
                ).append(x)
            return normal + dct + lst
        return data

    @model_serializer(when_used="json")
    def sort_model(self):
        data = super().model_dump()  # type: ignore[call-arg]
        return self.reorder_data(data)


_InternalSchema = TypeVar("_InternalSchema", bound=InternalSchema)
_PublicSchema = TypeVar("_PublicSchema", bound=PublicSchema)
