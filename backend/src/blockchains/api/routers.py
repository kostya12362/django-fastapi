from typing import Annotated, Optional

from django.db.models import Count
from fastapi import APIRouter, Depends, Path, status

from blockchains.api.schemas import (
    BlockSchemaResponse,
    CurrencySchemaResponse,
    ProviderSchemaResponse,
)
from blockchains.models import Block, Currency, Provider
from core.errors import HTTPException
from core.pagination import PageInfo, PaginationResponse, ParamsInput, paginate
from core.schemas import Response
from users.api.auth.security import user_auth

router = APIRouter(
    prefix="/blockchains",
    tags=["Blockchains"],
    dependencies=[Depends(user_auth.get_current_user)],
)

BlockId = Annotated[int, Path(..., title="Block number", alias="id", gt=0)]


@router.get(
    "/providers/",
    response_model=PaginationResponse[ProviderSchemaResponse, PageInfo],
    status_code=status.HTTP_200_OK,
)
async def get_all_providers(params: ParamsInput = Depends()):
    queryset = Provider.objects.annotate(block_count=Count("blocks"))
    return await paginate(queryset, params, ProviderSchemaResponse)


@router.get(
    "/currencies/",
    response_model=PaginationResponse[CurrencySchemaResponse, PageInfo],
    status_code=status.HTTP_200_OK,
)
async def providers(params: ParamsInput = Depends()):
    queryset = Currency.objects.annotate(block_count=Count("blocks"))
    return await paginate(queryset, params, CurrencySchemaResponse)


@router.get(
    "/blocks/",
    response_model=PaginationResponse[BlockSchemaResponse, PageInfo],
    status_code=status.HTTP_200_OK,
)
async def blocks(currency_name: Optional[str] = None, params: ParamsInput = Depends()):
    queryset = Block.objects.all()
    if currency_name:
        if await Currency.objects.filter(name=currency_name).aexists() is False:
            raise HTTPException(
                message=f'Currency "{currency_name}" not found',
                status_code=404,
                code="CURRENCY_NOT_FOUND",
            )
        queryset.filter(currency__name=currency_name)

    return await paginate(queryset, params, BlockSchemaResponse)


@router.get(
    "/blocks/{id}/",
    response_model=Response[BlockSchemaResponse],
    status_code=status.HTTP_200_OK,
)
async def get_block(block: BlockId) -> Response[BlockSchemaResponse]:
    obj = await Block.objects.filter(id=block).annotate().afirst()
    if obj is None:
        raise HTTPException(
            message="Block not found", status_code=404, code="BLOCK_NOT_FOUND"
        )
    return Response[BlockSchemaResponse](data=BlockSchemaResponse.model_validate(obj))
