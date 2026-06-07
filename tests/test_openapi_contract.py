from __future__ import annotations

import pytest


pytestmark = [
    pytest.mark.api,
    pytest.mark.docker,
    pytest.mark.contract,
]


def test_openapi_schema_is_available(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    body = response.json()

    assert body["openapi"].startswith("3.")
    assert "paths" in body
    assert "components" in body


def test_openapi_contains_product_paths(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/api/v1/products" in paths
    assert "/api/v1/products/categories" in paths
    assert "/api/v1/products/{product_id}" in paths
    assert "/api/v1/products/{product_id}/stock" in paths


def test_openapi_contains_payment_path(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/api/v1/payments/checkout" in paths


def test_openapi_product_create_response_contract(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    openapi = response.json()

    create_product = openapi["paths"]["/api/v1/products"]["post"]

    assert "requestBody" in create_product
    assert "responses" in create_product

    # Use 201 if you changed create route to status_code=201.
    # Use 200 if you kept default FastAPI behavior.
    assert "201" in create_product["responses"] or "200" in create_product["responses"]


def test_openapi_list_products_query_contract(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    openapi = response.json()

    list_products = openapi["paths"]["/api/v1/products"]["get"]

    parameters = {
        parameter["name"]: parameter
        for parameter in list_products["parameters"]
    }

    assert parameters["page"]["schema"]["minimum"] == 1
    assert parameters["limit"]["schema"]["minimum"] == 1
    assert parameters["limit"]["schema"]["default"] == 10

    sort_order_schema = parameters["sort_order"]["schema"]

    assert "enum" in sort_order_schema
    assert sort_order_schema["enum"] == ["asc", "desc"]