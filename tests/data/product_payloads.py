import uuid

from tests.schemas.requests import CreateProductRequest, UpdateProductRequest


def unique_product_name(prefix: str = "Test Product") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def create_product_request_data(
    name_prefix: str = "API Product",
    category: str = "Electronics",
    price: float = 99.99,
    quantity: int = 10,
) -> CreateProductRequest:
    return CreateProductRequest(
        name=unique_product_name(name_prefix),
        description="Product created from test framework",
        category=category,
        price=price,
        quantity=quantity,
    )


def update_product_request_data(
    name_prefix: str = "Updated Product",
    category: str = "Updated Category",
    price: float = 199.99,
    quantity: int = 25,
) -> UpdateProductRequest:
    return UpdateProductRequest(
        name=unique_product_name(name_prefix),
        description="Updated product description from test framework",
        category=category,
        price=price,
        quantity=quantity,
    )


def partial_update_price_request_data(
    price: float = 149.99,
) -> UpdateProductRequest:
    return UpdateProductRequest(price=price)


def partial_update_quantity_request_data(
    quantity: int = 5,
) -> UpdateProductRequest:
    return UpdateProductRequest(quantity=quantity)


def create_product_payload(
    name_prefix: str = "API Product",
    category: str = "Electronics",
    price: float = 99.99,
    quantity: int = 10,
) -> dict:
    request = create_product_request_data(
        name_prefix=name_prefix,
        category=category,
        price=price,
        quantity=quantity,
    )

    if hasattr(request, "model_dump"):
        return request.model_dump()

    return request.dict()


def update_product_payload(
    name_prefix: str = "Updated Product",
    category: str = "Updated Category",
    price: float = 199.99,
    quantity: int = 25,
) -> dict:
    request = update_product_request_data(
        name_prefix=name_prefix,
        category=category,
        price=price,
        quantity=quantity,
    )

    if hasattr(request, "model_dump"):
        return request.model_dump(exclude_none=True)

    return request.dict(exclude_none=True)