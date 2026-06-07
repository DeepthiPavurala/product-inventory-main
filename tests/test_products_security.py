from __future__ import annotations

import pytest

from tests.fakeapi.product_inventory import ProductInventory


pytestmark = [
    pytest.mark.api,
    pytest.mark.docker,
    pytest.mark.security,
    pytest.mark.negative,
]


def test_create_product_rejects_empty_name(client):
    product_api = ProductInventory(client)

    payload = {
        "name": "",
        "description": "Invalid empty name",
        "category": "Security",
        "price": 10.99,
        "quantity": 1,
    }

    response = product_api.create_product_expect_error(payload)

    assert response.status_code == 422
    assert response.data is not None


def test_create_product_rejects_empty_description(client):
    product_api = ProductInventory(client)

    payload = {
        "name": "Security Product",
        "description": "",
        "category": "Security",
        "price": 10.99,
        "quantity": 1,
    }

    response = product_api.create_product_expect_error(payload)

    assert response.status_code == 422
    assert response.data is not None


def test_create_product_rejects_empty_category(client):
    product_api = ProductInventory(client)

    payload = {
        "name": "Security Product",
        "description": "Invalid empty category",
        "category": "",
        "price": 10.99,
        "quantity": 1,
    }

    response = product_api.create_product_expect_error(payload)

    assert response.status_code == 422
    assert response.data is not None


def test_get_product_by_id_with_invalid_format_returns_not_found(client):
    product_api = ProductInventory(client)

    response = product_api.get_product_by_id_expect_error(
        "not-a-valid-id",
    )

    assert response.status_code == 404
    assert response.data is not None