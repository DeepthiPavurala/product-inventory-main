from typing import Literal, Optional
from pydantic import BaseModel, Field


class CreateProductRequest(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    category: str = Field(min_length=1)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)


class GetProductRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1)
    search: Optional[str] = None
    category: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: Literal["asc", "desc"] = "asc"


class UpdateProductRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = Field(default=None, min_length=1)
    category: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, gt=0)
    quantity: Optional[int] = Field(default=None, ge=0)