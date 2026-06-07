from __future__ import annotations

import uuid

import pytest

from tests.data.invalid_product_payloads import (
    CREATE_PRODUCT_BOUNDARY_CASES,
    CREATE_PRODUCT_EQUIVALENCE_CASES,
    INVALID_CREATE_PRODUCT_PAYLOADS,
    INVALID_SORT_ORDERS,
    INVALID_UPDATE_PRODUCT_PAYLOADS,
    PAGINATION_BOUNDARY_CASES,
    UPDATE_PRODUCT_BOUNDARY_CASES,
)
from tests.data.product_payloads import (
    create_product_request_data,
    partial_update_price_request_data,
    partial_update_quantity_request_data,
    update_product_request_data,
)
from tests.fakeapi.product_inventory import ProductInventory
from tests.schemas.requests import GetProductRequest


pytestmark = [
    pytest.mark.api,
    pytest.mark.integration,
]


class TestProductApi:
    @pytest.fixture(autouse=True)
    def setup_product_api(self, client):
        self.product_api = ProductInventory(client)

    def create_product_for_test(
        self,
        name_prefix: str = "Test Product",
        category: str = "Electronics",
        price: float = 99.99,
        quantity: int = 10,
    ):
        payload = create_product_request_data(
            name_prefix=name_prefix,
            category=category,
            price=price,
            quantity=quantity,
        )

        response = self.product_api.create_product(payload)

        assert response.status_code == 201
        assert response.data is not None

        return response.data, payload

    def create_raw_product_payload(
            self,
            name_prefix: str = "Raw Product",
            category: str = "Electronics",
            price: float = 99.99,
            quantity: int = 10,
    ) -> dict:
        return {
            "name": f"{name_prefix}-{uuid.uuid4().hex[:8]}",
            "description": "Raw product payload for invalid API testing",
            "category": category,
            "price": price,
            "quantity": quantity,
        }

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_create_product_valid(self):
        payload = create_product_request_data(name_prefix="Valid Product")

        response = self.product_api.create_product(payload)

        assert response.status_code == 201
        assert response.data is not None

        created_product = response.data

        assert created_product.id is not None
        assert created_product.name == payload.name
        assert created_product.description == payload.description
        assert created_product.category == payload.category
        assert created_product.price == payload.price
        assert created_product.quantity == payload.quantity

    @pytest.mark.negative
    @pytest.mark.regression
    def test_create_product_invalid_duplicate(self):
        payload = create_product_request_data(name_prefix="Duplicate Product")

        first_response = self.product_api.create_product(payload)

        assert first_response.status_code == 201
        assert first_response.data is not None

        duplicate_response = self.product_api.create_product_expect_error(payload)

        assert duplicate_response.status_code == 400
        assert duplicate_response.data is not None
        assert "already exists" in str(duplicate_response.data.detail)

    @pytest.mark.negative
    @pytest.mark.regression
    @pytest.mark.parametrize("invalid_payload", INVALID_CREATE_PRODUCT_PAYLOADS)
    def test_create_product_invalid_input(self, invalid_payload):
        response = self.product_api.create_product_expect_error(invalid_payload)

        assert response.status_code == 422
        assert response.data is not None
        assert response.data.detail is not None

    @pytest.mark.equivalence
    @pytest.mark.regression
    @pytest.mark.parametrize(
        ("price", "quantity", "expected_status"),
        CREATE_PRODUCT_EQUIVALENCE_CASES,
    )
    def test_create_product_equivalence_classes(
        self,
        price,
        quantity,
        expected_status,
    ):
        payload = self.create_raw_product_payload(
            name_prefix="Equivalence Product",
            price=price,
            quantity=quantity,
        )

        if expected_status == 201:
            response = self.product_api.create_product(payload)

            assert response.status_code == expected_status
            assert response.data is not None
            assert response.data.price == price
            assert response.data.quantity == quantity

        else:
            response = self.product_api.create_product_expect_error(payload)

            assert response.status_code == expected_status
            assert response.data is not None
            assert response.data.detail is not None

    @pytest.mark.boundary
    @pytest.mark.regression
    @pytest.mark.parametrize(
        ("price", "quantity", "expected_status"),
        CREATE_PRODUCT_BOUNDARY_CASES,
    )
    def test_create_product_boundary_values(
        self,
        price,
        quantity,
        expected_status,
    ):
        payload = self.create_raw_product_payload(
            name_prefix="Boundary Product",
            price=price,
            quantity=quantity,
        )

        if expected_status == 201:
            response = self.product_api.create_product(payload)

            assert response.status_code == expected_status
            assert response.data is not None
            assert response.data.price == price
            assert response.data.quantity == quantity

        else:
            response = self.product_api.create_product_expect_error(payload)

            assert response.status_code == expected_status
            assert response.data is not None
            assert response.data.detail is not None

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_get_products_paginated(self):
        category = f"Pagination-{uuid.uuid4().hex[:8]}"

        for index in range(7):
            self.create_product_for_test(
                name_prefix=f"Paginated Product {index}",
                category=category,
            )

        request = GetProductRequest(
            page=1,
            limit=5,
            category=category,
            sort_by="created_at",
            sort_order="asc",
        )

        response = self.product_api.get_products(request)

        assert response.status_code == 200
        assert response.data is not None

        products_page = response.data

        assert products_page.page == 1
        assert products_page.limit == 5
        assert products_page.total >= 7
        assert products_page.total_pages >= 2
        assert len(products_page.data) <= 5

        for product in products_page.data:
            assert product.category == category

    @pytest.mark.boundary
    @pytest.mark.regression
    @pytest.mark.parametrize(
        ("page", "limit", "expected_status"),
        PAGINATION_BOUNDARY_CASES,
    )
    def test_get_products_pagination_boundary_values(
        self,
        page,
        limit,
        expected_status,
    ):
        request = {
            "page": page,
            "limit": limit,
            "sort_by": "created_at",
            "sort_order": "asc",
        }

        if expected_status == 200:
            response = self.product_api.get_products(request)

            assert response.status_code == expected_status
            assert response.data is not None
            assert response.data.page == page
            assert response.data.limit == limit

        else:
            response = self.product_api.get_products_expect_error(request)

            assert response.status_code == expected_status
            assert response.data is not None
            assert response.data.detail is not None

    @pytest.mark.regression
    @pytest.mark.parametrize("sort_order", ["asc", "desc"])
    def test_get_products_valid_sort_order(self, sort_order):
        category = f"Sort-{uuid.uuid4().hex[:8]}"

        self.create_product_for_test(
            name_prefix="Sort Product One",
            category=category,
            price=50.00,
        )

        self.create_product_for_test(
            name_prefix="Sort Product Two",
            category=category,
            price=150.00,
        )

        request = GetProductRequest(
            page=1,
            limit=10,
            category=category,
            sort_by="price",
            sort_order=sort_order,
        )

        response = self.product_api.get_products(request)

        assert response.status_code == 200
        assert response.data is not None
        assert len(response.data.data) >= 2

    @pytest.mark.negative
    @pytest.mark.regression
    @pytest.mark.parametrize("invalid_sort_order", INVALID_SORT_ORDERS)
    def test_get_products_invalid_sort_order(self, invalid_sort_order):
        request = {
            "page": 1,
            "limit": 10,
            "sort_by": "created_at",
            "sort_order": invalid_sort_order,
        }

        response = self.product_api.get_products_expect_error(request)

        assert response.status_code == 422
        assert response.data is not None
        assert response.data.detail is not None

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_get_product_by_id_valid(self):
        created_product, _ = self.create_product_for_test(
            name_prefix="Get By Id Product",
        )

        response = self.product_api.get_product_by_id(created_product.id)

        assert response.status_code == 200
        assert response.data is not None

        product = response.data

        assert product.id == created_product.id
        assert product.name == created_product.name
        assert product.category == created_product.category

    @pytest.mark.negative
    @pytest.mark.regression
    def test_get_product_by_id_invalid(self):
        invalid_product_id = str(uuid.uuid4())

        response = self.product_api.get_product_by_id_expect_error(invalid_product_id)

        assert response.status_code == 404
        assert response.data is not None
        assert response.data.detail == "Product not found"

    @pytest.mark.regression
    def test_get_products_by_category_valid(self):
        category = f"Category-{uuid.uuid4().hex[:8]}"

        created_product, _ = self.create_product_for_test(
            name_prefix="Category Product",
            category=category,
        )

        response = self.product_api.get_products_by_category(category)

        assert response.status_code == 200
        assert response.data is not None

        products_page = response.data

        assert products_page.total >= 1

        product_ids = [product.id for product in products_page.data]

        assert created_product.id in product_ids

        for product in products_page.data:
            assert product.category == category

    @pytest.mark.negative
    @pytest.mark.regression
    def test_get_products_by_category_unknown_returns_empty(self):
        unknown_category = f"Unknown-{uuid.uuid4().hex[:8]}"

        response = self.product_api.get_products_by_category(unknown_category)

        assert response.status_code == 200
        assert response.data is not None
        assert response.data.total == 0
        assert response.data.data == []

    @pytest.mark.regression
    def test_get_products_by_name_valid(self):
        created_product, _ = self.create_product_for_test(
            name_prefix="Searchable Product",
        )

        response = self.product_api.get_products_by_name(created_product.name)

        assert response.status_code == 200
        assert response.data is not None
        assert response.data.total >= 1

        product_names = [product.name for product in response.data.data]

        assert created_product.name in product_names

    @pytest.mark.negative
    @pytest.mark.regression
    def test_get_products_by_name_unknown_returns_empty(self):
        unknown_name = f"NoSuchProduct-{uuid.uuid4().hex[:8]}"

        response = self.product_api.get_products_by_name(unknown_name)

        assert response.status_code == 200
        assert response.data is not None
        assert response.data.total == 0
        assert response.data.data == []

    @pytest.mark.regression
    def test_get_product_categories_valid(self):
        category = f"CategoryList-{uuid.uuid4().hex[:8]}"

        self.create_product_for_test(
            name_prefix="Category List Product",
            category=category,
        )

        response = self.product_api.get_product_categories()

        assert response.status_code == 200
        assert response.data is not None
        assert isinstance(response.data, list)
        assert category in response.data

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_update_product_valid(self):
        created_product, _ = self.create_product_for_test(
            name_prefix="Update Target Product",
        )

        update_payload = update_product_request_data(
            name_prefix="Updated Product",
            category="Updated Category",
            price=199.99,
            quantity=25,
        )

        response = self.product_api.update_product(
            product_id=created_product.id,
            update_request=update_payload,
        )

        assert response.status_code == 200
        assert response.data is not None

        updated_product = response.data

        assert updated_product.id == created_product.id
        assert updated_product.name == update_payload.name
        assert updated_product.description == update_payload.description
        assert updated_product.category == update_payload.category
        assert updated_product.price == update_payload.price
        assert updated_product.quantity == update_payload.quantity

    @pytest.mark.regression
    def test_update_product_partial_valid(self):
        created_product, _ = self.create_product_for_test(
            name_prefix="Partial Update Product",
        )

        update_payload = partial_update_price_request_data(price=149.99)

        response = self.product_api.update_product(
            product_id=created_product.id,
            update_request=update_payload,
        )

        assert response.status_code == 200
        assert response.data is not None

        updated_product = response.data

        assert updated_product.id == created_product.id
        assert updated_product.price == 149.99
        assert updated_product.name == created_product.name
        assert updated_product.description == created_product.description
        assert updated_product.category == created_product.category

    @pytest.mark.regression
    def test_update_product_partial_quantity_valid(self):
        created_product, _ = self.create_product_for_test(
            name_prefix="Partial Update Product Quantity",
        )

        update_payload = partial_update_quantity_request_data(quantity=8)

        response = self.product_api.update_product(
            product_id=created_product.id,
            update_request=update_payload,
        )

        assert response.status_code == 200
        assert response.data is not None

        updated_product = response.data

        assert updated_product.id == created_product.id
        assert updated_product.quantity == 8
        assert updated_product.name == created_product.name
        assert updated_product.description == created_product.description
        assert updated_product.category == created_product.category

    @pytest.mark.negative
    @pytest.mark.regression
    @pytest.mark.parametrize("invalid_payload", INVALID_UPDATE_PRODUCT_PAYLOADS)
    def test_update_product_invalid_input(self, invalid_payload):
        created_product, _ = self.create_product_for_test(
            name_prefix="Invalid Update Product Price",
        )

        response = self.product_api.update_product_expect_error(
            product_id=created_product.id,
            update_request=invalid_payload,
        )

        assert response.status_code == 422
        assert response.data is not None
        assert response.data.detail is not None



    @pytest.mark.boundary
    @pytest.mark.regression
    @pytest.mark.parametrize(
        ("update_payload", "expected_status"),
        UPDATE_PRODUCT_BOUNDARY_CASES,
    )
    def test_update_product_boundary_values(self, update_payload, expected_status):
        created_product, _ = self.create_product_for_test(
            name_prefix="Update Boundary Product",
        )

        if expected_status == 200:
            response = self.product_api.update_product(
                product_id=created_product.id,
                update_request=update_payload,
            )

            assert response.status_code == expected_status
            assert response.data is not None

            if "price" in update_payload:
                assert response.data.price == update_payload["price"]

            if "quantity" in update_payload:
                assert response.data.quantity == update_payload["quantity"]

        else:
            response = self.product_api.update_product_expect_error(
                product_id=created_product.id,
                update_request=update_payload,
            )

            assert response.status_code == expected_status
            assert response.data is not None
            assert response.data.detail is not None

    @pytest.mark.negative
    @pytest.mark.regression
    def test_update_product_invalid_id(self):
        invalid_product_id = str(uuid.uuid4())

        update_payload = update_product_request_data(
            name_prefix="Invalid Id Update",
        )

        response = self.product_api.update_product_expect_error(
            product_id=invalid_product_id,
            update_request=update_payload,
        )

        assert response.status_code == 404
        assert response.data is not None
        assert response.data.detail == "Product not found"

    @pytest.mark.regression
    def test_adjust_stock_valid_adds_quantity(self):
        created_product, _ = self.create_product_for_test(
            name_prefix="Stock Add Product",
            quantity=10,
        )

        response = self.product_api.adjust_stock(
            product_id=created_product.id,
            delta=5,
        )

        assert response.status_code == 200
        assert response.data is not None

        updated_product = response.data

        assert updated_product.id == created_product.id
        assert updated_product.quantity == 15
        assert isinstance(updated_product.low_stock_alert_sent, bool)

    @pytest.mark.regression
    def test_adjust_stock_valid_reduces_quantity_and_checks_low_stock_flag(self):
        created_product, _ = self.create_product_for_test(
            name_prefix="Low Stock Adjustment Product",
            quantity=10,
        )

        response = self.product_api.adjust_stock(
            product_id=created_product.id,
            delta=-8,
        )

        assert response.status_code == 200
        assert response.data is not None

        updated_product = response.data

        assert updated_product.id == created_product.id
        assert updated_product.quantity == 2
        assert isinstance(updated_product.low_stock_alert_sent, bool)

    @pytest.mark.negative
    @pytest.mark.regression
    def test_adjust_stock_invalid_negative_result(self):
        created_product, _ = self.create_product_for_test(
            name_prefix="Negative Stock Product",
            quantity=5,
        )

        response = self.product_api.adjust_stock_expect_error(
            product_id=created_product.id,
            delta=-6,
        )

        assert response.status_code == 400
        assert response.data is not None
        assert "negative" in str(response.data.detail).lower()

    @pytest.mark.negative
    @pytest.mark.regression
    def test_adjust_stock_invalid_id(self):
        invalid_product_id = str(uuid.uuid4())

        response = self.product_api.adjust_stock_expect_error(
            product_id=invalid_product_id,
            delta=5,
        )

        assert response.status_code == 404
        assert response.data is not None
        assert response.data.detail == "Product not found"

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_soft_delete_product_valid_and_verify_not_returned_by_get_id(self):
        created_product, _ = self.create_product_for_test(
            name_prefix="Soft Delete Product",
        )

        delete_response = self.product_api.soft_delete_product(created_product.id)

        assert delete_response.status_code == 200
        assert delete_response.data is not None
        assert delete_response.data.message == "Product deleted"

        get_response = self.product_api.get_product_by_id_expect_error(
            created_product.id
        )

        assert get_response.status_code == 404
        assert get_response.data is not None
        assert get_response.data.detail == "Product not found"

    @pytest.mark.regression
    def test_soft_delete_product_valid_and_verify_not_returned_by_list(self):
        created_product, _ = self.create_product_for_test(
            name_prefix="Soft Delete List Product",
        )

        delete_response = self.product_api.soft_delete_product(created_product.id)

        assert delete_response.status_code == 200
        assert delete_response.data is not None

        search_response = self.product_api.get_products_by_name(created_product.name)

        assert search_response.status_code == 200
        assert search_response.data is not None
        assert search_response.data.total == 0
        assert search_response.data.data == []

    @pytest.mark.negative
    @pytest.mark.regression
    def test_soft_delete_product_invalid_id(self):
        invalid_product_id = str(uuid.uuid4())

        response = self.product_api.soft_delete_product_expect_error(
            invalid_product_id
        )

        assert response.status_code == 404
        assert response.data is not None
        assert response.data.detail == "Product not found"

    @pytest.mark.integration
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_product_lifecycle_integration_flow(self):
        create_payload = create_product_request_data(
            name_prefix="Lifecycle Product",
            quantity=20,
            price=100.00,
        )

        create_response = self.product_api.create_product(create_payload)

        assert create_response.status_code == 201
        assert create_response.data is not None

        product_id = create_response.data.id

        get_response = self.product_api.get_product_by_id(product_id)

        assert get_response.status_code == 200
        assert get_response.data is not None
        assert get_response.data.id == product_id
        assert get_response.data.name == create_payload.name

        update_payload = update_product_request_data(
            name_prefix="Lifecycle Updated Product",
            category="Lifecycle Updated Category",
            price=150.00,
            quantity=25,
        )

        update_response = self.product_api.update_product(
            product_id=product_id,
            update_request=update_payload,
        )

        assert update_response.status_code == 200
        assert update_response.data is not None
        assert update_response.data.id == product_id
        assert update_response.data.name == update_payload.name
        assert update_response.data.price == update_payload.price
        assert update_response.data.quantity == update_payload.quantity

        stock_response = self.product_api.adjust_stock(
            product_id=product_id,
            delta=-20,
        )

        assert stock_response.status_code == 200
        assert stock_response.data is not None
        assert stock_response.data.id == product_id
        assert stock_response.data.quantity == 5
        assert isinstance(stock_response.data.low_stock_alert_sent, bool)

        delete_response = self.product_api.soft_delete_product(product_id)

        assert delete_response.status_code == 200
        assert delete_response.data is not None
        assert delete_response.data.message == "Product deleted"

        get_deleted_response = self.product_api.get_product_by_id_expect_error(
            product_id
        )

        assert get_deleted_response.status_code == 404
        assert get_deleted_response.data is not None
        assert get_deleted_response.data.detail == "Product not found"