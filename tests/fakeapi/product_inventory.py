from __future__ import annotations

from typing import Any

from tests.utils.api_paths import api_routes

from tests.fakeapi.request_client import ApiResponse, RequestClient
from tests.schemas.requests import (
    CreateProductRequest,
    GetProductRequest,
    UpdateProductRequest,
)
from tests.schemas.responses import (
    ErrorResponse,
    ProductDeleteResponse,
    ProductListResponse,
    ProductResponse,
    ProductStockAdjustmentResponse,
)
from tests.utils.payload_converter import to_payload


class ProductInventory:
    def __init__(self, client: RequestClient) -> None:
        self.client = client

    def create_product(
        self,
        create_request: CreateProductRequest | dict[str, Any],
    ) -> ApiResponse[ProductResponse]:
        payload = to_payload(create_request)

        return self.client.post(
            path=api_routes.products,
            json=payload,
            response_model=ProductResponse,
        )

    def create_product_expect_error(
        self,
        create_request: CreateProductRequest | dict[str, Any],
    ) -> ApiResponse[ErrorResponse]:
        payload = to_payload(create_request)

        return self.client.post(
            path=api_routes.products,
            json=payload,
            response_model=ErrorResponse,
        )

    def get_products(
        self,
        get_request: GetProductRequest | dict[str, Any] | None = None,
    ) -> ApiResponse[ProductListResponse]:
        if get_request is None:
            get_request = GetProductRequest()

        params = to_payload(get_request)

        return self.client.get(
            path=api_routes.products,
            params=params,
            response_model=ProductListResponse,
        )

    def get_products_expect_error(
        self,
        get_request: GetProductRequest | dict[str, Any],
    ) -> ApiResponse[ErrorResponse]:
        params = to_payload(get_request)

        return self.client.get(
            path=api_routes.products,
            params=params,
            response_model=ErrorResponse,
        )

    def get_product_by_id(
        self,
        product_id: str,
    ) -> ApiResponse[ProductResponse]:
        return self.client.get(
            path=api_routes.product_detail(product_id),
            response_model=ProductResponse,
        )

    def get_product_by_id_expect_error(
        self,
        product_id: str,
    ) -> ApiResponse[ErrorResponse]:
        return self.client.get(
            path=api_routes.product_detail(product_id),
            response_model=ErrorResponse,
        )

    def get_products_by_category(
        self,
        category: str,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "asc",
    ) -> ApiResponse[ProductListResponse]:
        request = GetProductRequest(
            page=page,
            limit=limit,
            category=category,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return self.get_products(request)

    def get_products_by_name(
        self,
        name: str,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "asc",
    ) -> ApiResponse[ProductListResponse]:
        request = GetProductRequest(
            page=page,
            limit=limit,
            search=name,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return self.get_products(request)

    def get_product_categories(self) -> ApiResponse[list[str]]:
        return self.client.get(
            path=api_routes.product_categories,
            response_model=list[str],
        )

    def update_product(
        self,
        product_id: str,
        update_request: UpdateProductRequest | dict[str, Any],
    ) -> ApiResponse[ProductResponse]:
        payload = to_payload(update_request)

        return self.client.patch(
            path=api_routes.product_detail(product_id),
            json=payload,
            response_model=ProductResponse,
        )

    def update_product_expect_error(
        self,
        product_id: str,
        update_request: UpdateProductRequest | dict[str, Any],
    ) -> ApiResponse[ErrorResponse]:
        payload = to_payload(update_request)

        return self.client.patch(
            path=api_routes.product_detail(product_id),
            json=payload,
            response_model=ErrorResponse,
        )

    def soft_delete_product(
        self,
        product_id: str,
    ) -> ApiResponse[ProductDeleteResponse]:
        return self.client.delete(
            path=api_routes.product_detail(product_id),
            response_model=ProductDeleteResponse,
        )

    def soft_delete_product_expect_error(
        self,
        product_id: str,
    ) -> ApiResponse[ErrorResponse]:
        return self.client.delete(
            path=api_routes.product_detail(product_id),
            response_model=ErrorResponse,
        )

    def adjust_stock(
        self,
        product_id: str,
        delta: int,
    ) -> ApiResponse[ProductStockAdjustmentResponse]:
        return self.client.patch(
            path=api_routes.product_stock(product_id),
            json={"delta": delta},
            response_model=ProductStockAdjustmentResponse,
        )

    def adjust_stock_expect_error(
        self,
        product_id: str,
        delta: int,
    ) -> ApiResponse[ErrorResponse]:
        return self.client.patch(
            path=api_routes.product_stock(product_id),
            json={"delta": delta},
            response_model=ErrorResponse,
        )