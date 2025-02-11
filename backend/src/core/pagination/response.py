from typing import Generic, Optional, TypeVar

from pydantic import Field

from core.schemas import PublicSchema, ResponseMulti, _PublicSchema


class ParamsInput(PublicSchema):
    page: int = Field(1, ge=1)
    limit: int = Field(100, ge=1, le=100)
    skip: Optional[int] = Field(0, ge=0)


class Page(ParamsInput):
    count: int
    next: Optional[str]
    previous: Optional[str]


class PageInfo(ParamsInput):
    count: int
    next: Optional[str]
    previous: Optional[str]


# _PublicSchema = TypeVar("_PublicSchema", bound=PublicSchema)
_PageInfo = TypeVar("_PageInfo", bound=PageInfo)


class PaginationResponse(
    ResponseMulti[_PublicSchema], Generic[_PublicSchema, _PageInfo]
):
    """Base class for pagination responses."""

    total: int
    page_info: _PageInfo
