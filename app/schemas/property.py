from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PropertyBase(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    country: str = Field(default="Nigeria", min_length=2, max_length=100)
    total_units: int = Field(default=0, ge=0)
    manager_id: int = Field(gt=0)

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("name", "address", "city", "state", "country", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, min_length=1)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    country: str | None = Field(default=None, min_length=2, max_length=100)
    total_units: int | None = Field(default=None, ge=0)
    manager_id: int | None = Field(default=None, gt=0)

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        return value.strip().upper() if value is not None else value

    @field_validator("name", "address", "city", "state", "country", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value


class PropertyRead(PropertyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
