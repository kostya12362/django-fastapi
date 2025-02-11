from typing import Any, Mapping, Optional

from django.db.models import QuerySet
from fastapi import Request

from core.pagination.response import (
    PageInfo,
    PaginationResponse,
    ParamsInput,
    PublicSchema,
)
from core.utils import params_from_base, request


def _update_path(
    req: Request, to_update: Optional[Mapping[str, Any]] = None
) -> str | None:
    url = req.url.replace_query_params(**params_from_base(req.query_params))
    if to_update is None:
        return None
    url = url.include_query_params(**to_update)
    return str(url)


async def paginate(
    queryset: QuerySet, params: ParamsInput, schema: type[PublicSchema]
) -> PaginationResponse:
    """Function to paginate a queryset.
    On the future we can add more params to the function."""

    total = await queryset.acount()

    # Calculate the offset
    page, limit, skip = params.page, params.limit, params.skip or 0
    offset = (page - 1) * limit + skip
    total_pages = (total + limit - 1) // limit

    # Create object `PageInfo`
    page_info = PageInfo(
        count=total_pages,
        page=page,
        limit=limit,
        skip=skip,
        next=_update_path(
            req=request(), to_update={"page": page + 1} if page < total_pages else None
        ),
        previous=_update_path(
            req=request(), to_update={"page": page - 1} if page > 1 else None
        ),
    )

    data = [
        schema.model_validate(obj) async for obj in queryset[offset : offset + limit]
    ]
    return PaginationResponse(total=total, data=data, page_info=page_info)
