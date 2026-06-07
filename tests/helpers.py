"""Reusable test helper functions."""

from __future__ import annotations

import uuid

from app.models.product import Product


def unique_product_payload(quantity: int = 5) -> dict:
    suffix = uuid.uuid4().hex[:8]
    return {
        "name": f"Test Laptop {suffix}",
        "description": "Testing laptop",
        "category": "Testing",
        "price": 1000,
        "quantity": quantity,
    }


def product_model(name: str = "Test Product", quantity: int = 5) -> Product:
    return Product(
        id=str(uuid.uuid4()),
        name=name,
        description="Unit-test product",
        category="Testing",
        price=10.00,
        quantity=quantity,
        is_active=True,
    )
