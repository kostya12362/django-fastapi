from datetime import datetime
from typing import Any

from django.db.utils import IntegrityError
from loguru import logger

from blockchains.models import Block, Currency, Provider
from core.broker import BrokerRegistry

registry = BrokerRegistry()


@registry.rpc(method_name="save_provider")
async def save_provider(name: str) -> int | None:
    try:
        obj, _ = await Provider.objects.aupdate_or_create(name=name)
        return obj.id
    except IntegrityError:
        logger.info(f"Provider {name} already exists")
        return None


@registry.rpc(method_name="get_provider")
async def get_provider(provider_id: int) -> dict[str, Any] | None:
    try:
        obj = await Provider.objects.aget(id=provider_id)
        return {
            "id": obj.id,
            "name": obj.name,
            "api_key": obj.api_key,
        }
    except Provider.DoesNotExist:
        return None


@registry.rpc(method_name="save_currency")
async def save_currency(name: str) -> int | None:
    try:
        obj, _ = await Currency.objects.aupdate_or_create(name=name)
        return obj.id
    except IntegrityError:
        logger.info(f"Provider {name} already exists")
        return None


@registry.consumer(queue_name="blockchains:save_block", num_consumers=3)
async def save_block_number(
    block_number: int,
    provider_id: int,
    currency_id: int,
    created_at: datetime,
) -> None:
    try:
        await Block.objects.acreate(
            block_number=block_number,
            provider_id=provider_id,
            currency_id=currency_id,
            created_at=created_at,
        )
        logger.info(
            f"block_number: {block_number}, provider_id: {provider_id},"
            f" currency_id: {currency_id}, created_at: {created_at}"
        )
    except IntegrityError:
        pass
