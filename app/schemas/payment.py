from pydantic import BaseModel, Field


class CheckoutSessionRequest(BaseModel):
    product_id: str
    product_name: str
    unit_amount: int = Field(gt=0, description="Amount in the smallest currency unit, for example cents.")
    quantity: int = Field(default=1, ge=1)
    currency: str = Field(default="usd", min_length=3, max_length=3)


class CheckoutSessionResponse(BaseModel):
    checkout_session_id: str
    checkout_url: str
