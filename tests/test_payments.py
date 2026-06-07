from __future__ import annotations

import importlib
import os

import pytest
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.core.api_paths import api_routes

pytestmark = pytest.mark.unit

# app.core.config requires DATABASE_URL at import time. The payment endpoint does
# not touch the database, but the app imports the global settings during startup.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from app import main as app_main  # noqa: E402


def test_checkout_endpoint_mocks_stripe_session(monkeypatch):
    def fake_create_checkout_session(payload):
        assert payload.product_id == "prod_123"
        assert payload.product_name == "Mocked Laptop"
        assert payload.unit_amount == 4999
        return SimpleNamespace(
            id="cs_test_mocked_123",
            url="https://checkout.stripe.com/c/pay/cs_test_mocked_123",
        )

    monkeypatch.setattr(
        "app.api.routes.payment.create_checkout_session",
        fake_create_checkout_session,
    )

    client = TestClient(app_main.app)
    response = client.post(
        api_routes.payment_checkout,
        json={
            "product_id": "prod_123",
            "product_name": "Mocked Laptop",
            "unit_amount": 4999,
            "quantity": 1,
            "currency": "usd",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "checkout_session_id": "cs_test_mocked_123",
        "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_mocked_123",
    }


def test_payment_service_mocks_stripe_sdk(monkeypatch):
    payment_service = importlib.import_module("app.services.payment_service")
    payment_schema = importlib.import_module("app.schemas.payment")

    calls = []

    def fake_stripe_create(**kwargs):
        calls.append(kwargs)
        return {"id": "cs_test_sdk_mock", "url": "https://checkout.stripe.com/mock"}

    monkeypatch.setattr(payment_service.stripe.checkout.Session, "create", fake_stripe_create)

    payload = payment_schema.CheckoutSessionRequest(
        product_id="prod_456",
        product_name="Mocked Headphones",
        unit_amount=2599,
        quantity=2,
        currency="usd",
    )

    session = payment_service.create_checkout_session(payload)

    assert session["id"] == "cs_test_sdk_mock"
    assert calls[0]["mode"] == "payment"
    assert calls[0]["metadata"] == {"product_id": "prod_456"}
    assert calls[0]["line_items"][0]["price_data"]["unit_amount"] == 2599
    assert calls[0]["line_items"][0]["quantity"] == 2

def test_create_checkout_missing_body_returns_422(client):
    response = client.post(
        "/api/v1/payments/checkout",
        json={},
    )

    assert response.status_code == 422


def test_create_checkout_invalid_quantity_returns_422(client):
    payload = {
        "product_id": "test-product-id",
        "quantity": 0,
    }

    response = client.post(
        "/api/v1/payments/checkout",
        json=payload,
    )

    assert response.status_code == 422


def test_create_checkout_negative_quantity_returns_422(client):
    payload = {
        "product_id": "test-product-id",
        "quantity": -1,
    }

    response = client.post(
        "/api/v1/payments/checkout",
        json=payload,
    )

    assert response.status_code == 422


def test_create_checkout_missing_line_items_returns_422(client):
    response = client.post(
        "/api/v1/payments/checkout",
        json={},
    )

    assert response.status_code == 422


def test_create_checkout_empty_line_items_returns_422(client):
    response = client.post(
        "/api/v1/payments/checkout",
        json={"line_items": []},
    )

    assert response.status_code == 422
