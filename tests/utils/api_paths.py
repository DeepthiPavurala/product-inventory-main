API_PREFIX = "/api/v1"

HEALTH_PATH = "/health"
PRODUCTS_PATH = "/products"
PRODUCT_CATEGORIES_PATH = "/products/categories"


class ApiRoutes:
    @property
    def products(self) -> str:
        return f"{API_PREFIX}{PRODUCTS_PATH}"

    @property
    def product_categories(self) -> str:
        return f"{API_PREFIX}{PRODUCT_CATEGORIES_PATH}"

    def product_detail(self, product_id: str) -> str:
        return f"{API_PREFIX}{PRODUCTS_PATH}/{product_id}"

    def product_stock(self, product_id: str) -> str:
        return f"{API_PREFIX}{PRODUCTS_PATH}/{product_id}/stock"


api_routes = ApiRoutes()