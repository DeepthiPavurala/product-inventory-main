from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    category: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, ge=0)


class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockAdjustment(BaseModel):
    delta: int


class StockResponse(BaseModel):
    id: str
    name: str
    quantity: int = Field(ge=0)
    low_stock_alert_sent: bool

class ProductDeleteResponse(BaseModel):
    message: str
