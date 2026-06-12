from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class DSSItemInput(BaseModel):
    item_id: int = Field(gt=0)
    title: str | None = Field(default=None, max_length=255)
    urgency: Decimal = Field(ge=1, le=10)
    impact: Decimal = Field(ge=1, le=10)
    asset_importance: Decimal = Field(ge=1, le=10)
    cost: Decimal = Field(ge=0)

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value


class DSSRankingRequest(BaseModel):
    items: list[DSSItemInput] = Field(min_length=1)


class DSSRankedItem(BaseModel):
    rank: int
    item_id: int
    title: str | None
    urgency: Decimal
    impact: Decimal
    asset_importance: Decimal
    cost: Decimal
    cost_factor: Decimal
    priority_score: Decimal
    recommendation: str


class DSSRankingResponse(BaseModel):
    formula: str
    items: list[DSSRankedItem]
