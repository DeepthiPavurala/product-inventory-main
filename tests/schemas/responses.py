from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


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


class ProductListResponse(BaseModel):
    data: list[ProductResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    limit: int = Field(ge=1)
    total_pages: int = Field(ge=0)


class ProductDeleteResponse(BaseModel):
    message: str


class ProductStockAdjustmentResponse(BaseModel):
    id: str
    name: str
    quantity: int = Field(ge=0)
    low_stock_alert_sent: bool


class ErrorResponse(BaseModel):
    detail: Any