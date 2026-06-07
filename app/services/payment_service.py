from __future__ import annotations

import stripe
from fastapi import HTTPException

from app.schemas.payment import CheckoutSessionRequest


DEFAULT_SUCCESS_URL = "http://localhost:3000/payment/success"
DEFAULT_CANCEL_URL = "http://localhost:3000/payment/cancel"


def create_checkout_session(
    payload: CheckoutSessionRequest,
    *,
    success_url: str = DEFAULT_SUCCESS_URL,
    cancel_url: str = DEFAULT_CANCEL_URL,
):
    """Create a Stripe Checkout Session for buying inventory products.

    Tests should mock this function or stripe.checkout.Session.create so that no
    real Stripe API calls or real charges are attempted during automated tests.
    """
    try:
        return stripe.checkout.Session.create(
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=[
                {
                    "price_data": {
                        "currency": payload.currency,
                        "product_data": {"name": payload.product_name},
                        "unit_amount": payload.unit_amount,
                    },
                    "quantity": payload.quantity,
                }
            ],
            metadata={"product_id": payload.product_id},
        )
    except stripe.error.StripeError as exc:
        raise HTTPException(status_code=502, detail=f"Stripe checkout failed: {exc.user_message or str(exc)}") from exc
