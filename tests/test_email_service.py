from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services.email_service import (
    build_low_stock_email,
    notify_if_low_stock,
    should_send_low_stock_alert,
)


def product_model(
    name: str = "Test Product",
    quantity: int = 5,
):
    return SimpleNamespace(
        name=name,
        quantity=quantity,
    )


@pytest.mark.unit
@pytest.mark.boundary
def test_should_send_low_stock_alert_uses_threshold_boundaries():
    assert should_send_low_stock_alert(quantity=5, threshold=5) is True
    assert should_send_low_stock_alert(quantity=6, threshold=5) is False
    assert should_send_low_stock_alert(quantity=4, threshold=5) is True


@pytest.mark.unit
def test_should_send_low_stock_alert_returns_false_when_quantity_above_threshold():
    assert should_send_low_stock_alert(quantity=10, threshold=5) is False


@pytest.mark.unit
def test_build_low_stock_email_contains_product_context():
    product = product_model(
        name="USB Cable",
        quantity=2,
    )

    message = build_low_stock_email(product)

    assert message["Subject"] == "Low stock alert: USB Cable"
    assert "USB Cable" in message.get_content()
    assert "Current quantity: 2" in message.get_content()


@pytest.mark.unit
def test_notify_if_low_stock_sends_email_when_quantity_is_low(monkeypatch):
    product = product_model(
        name="Wireless Mouse",
        quantity=1,
    )

    sent_products = []

    def fake_send_low_stock_email(product_to_send):
        sent_products.append(product_to_send.name)

    monkeypatch.setattr(
        "app.services.email_service.send_low_stock_email",
        fake_send_low_stock_email,
    )

    result = notify_if_low_stock(product)

    assert result is True
    assert sent_products == ["Wireless Mouse"]


@pytest.mark.unit
def test_notify_if_low_stock_does_not_send_email_when_quantity_is_high(monkeypatch):
    product = product_model(
        name="Keyboard",
        quantity=20,
    )

    sent_products = []

    def fake_send_low_stock_email(product_to_send):
        sent_products.append(product_to_send.name)

    monkeypatch.setattr(
        "app.services.email_service.send_low_stock_email",
        fake_send_low_stock_email,
    )

    result = notify_if_low_stock(product)

    assert result is False
    assert sent_products == []