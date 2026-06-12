from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PropertyFundBase(BaseModel):
    property_id: int = Field(gt=0)
    fiscal_year: int = Field(ge=2000, le=2100)
    annual_budget: Decimal = Field(default=Decimal("0.00"), ge=0)
    current_balance: Decimal = Field(default=Decimal("0.00"), ge=0)
    reserved_balance: Decimal = Field(default=Decimal("0.00"), ge=0)
    currency: str = Field(default="NGN", min_length=3, max_length=3)

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.strip().upper()

    @model_validator(mode="after")
    def validate_reserved_balance(self) -> "PropertyFundBase":
        if self.reserved_balance > self.current_balance:
            raise ValueError("reserved_balance cannot exceed current_balance")
        return self


class PropertyFundCreate(PropertyFundBase):
    pass


class PropertyFundUpdate(BaseModel):
    fiscal_year: int | None = Field(default=None, ge=2000, le=2100)
    annual_budget: Decimal | None = Field(default=None, ge=0)
    current_balance: Decimal | None = Field(default=None, ge=0)
    reserved_balance: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return value.strip().upper() if value is not None else value


class PropertyFundRead(PropertyFundBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
