from datetime import datetime

from pydantic import Field

from core.schemas import PublicSchema


class BlockSchemaResponse(PublicSchema):
    id: int = Field(..., title="Block id")
    block_number: int = Field(..., title="Block number")
    provider_id: int = Field(
        ...,
        title="Provider id",
    )
    currency_id: int = Field(..., title="Currency id")
    created_at: datetime = Field(..., title="Block created at")
    stored_at: datetime = Field(..., title="Block stored at")


class ProviderSchemaResponse(PublicSchema):
    id: int = Field(..., title="Provider id")
    name: str = Field(..., title="Provider name")
    block_count: int = Field(..., title="Block count")


class CurrencySchemaResponse(ProviderSchemaResponse):
    id: int = Field(..., title="Currency id")
    name: str = Field(..., title="Currency name")


class BlockDetailSchemaResponse(BlockSchemaResponse):
    id: int
    block_number: int
    provider: ProviderSchemaResponse
    currency: int
