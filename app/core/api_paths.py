"""Shared API route constants and builders.

Keep route strings in one place so app registration, tests, scripts, and future
clients do not duplicate hardcoded endpoint paths such as `/api/v1/products`.
"""

from __future__ import annotations

from dataclasses import dataclass

ROOT_PATH = "/"
API_PREFIX = "/api/v1"
HEALTH_PATH = "/health"

PRODUCTS_PREFIX = "/products"
PRODUCT_CATEGORIES_PATH = "/categories"
PAYMENTS_PREFIX = "/payments"
PAYMENT_CHECKOUT_PATH = "/checkout"


@dataclass(frozen=True)
class ApiRouteBuilder:
    """Build fully qualified API paths from shared route fragments."""

    api_prefix: str = API_PREFIX

    def _join(self, *parts: str) -> str:
        cleaned = [part.strip("/") for part in parts if part]
        return "/" + "/".join(cleaned)

    @property
    def health(self) -> str:
        return HEALTH_PATH

    @property
    def api_root(self) -> str:
        return self.api_prefix

    @property
    def products(self) -> str:
        return self._join(self.api_prefix, PRODUCTS_PREFIX)

    @property
    def product_categories(self) -> str:
        return self._join(self.products, PRODUCT_CATEGORIES_PATH)

    def product_detail(self, product_id: str) -> str:
        return self._join(self.products, product_id)

    def product_stock(self, product_id: str) -> str:
        return self._join(self.products, product_id, "stock")

    @property
    def payments(self) -> str:
        return self._join(self.api_prefix, PAYMENTS_PREFIX)

    @property
    def payment_checkout(self) -> str:
        return self._join(self.payments, PAYMENT_CHECKOUT_PATH)


api_routes = ApiRouteBuilder()
