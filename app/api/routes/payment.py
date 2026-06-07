from fastapi import APIRouter, HTTPException, status

from app.schemas.payment import CheckoutSessionRequest, CheckoutSessionResponse
from app.core.api_paths import PAYMENTS_PREFIX, PAYMENT_CHECKOUT_PATH
from app.services.payment_service import create_checkout_session

router = APIRouter(prefix=PAYMENTS_PREFIX, tags=["Payments"])


@router.post(PAYMENT_CHECKOUT_PATH, response_model=CheckoutSessionResponse, summary="Create Checkout")
def create_checkout(payload: CheckoutSessionRequest):
    session = create_checkout_session(payload)
    checkout_url = getattr(session, "url", None) or session.get("url")
    checkout_session_id = getattr(session, "id", None) or session.get("id")

    if not checkout_url or not checkout_session_id:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Stripe did not return a checkout session URL")

    return CheckoutSessionResponse(
        checkout_session_id=checkout_session_id,
        checkout_url=checkout_url,
    )
