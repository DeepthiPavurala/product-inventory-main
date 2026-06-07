INVALID_CREATE_PRODUCT_PAYLOADS = [
    {
        "name": "Invalid Price Zero",
        "description": "Invalid product",
        "category": "Testing",
        "price": 0,
        "quantity": 10,
    },
    {
        "name": "Invalid Price Negative",
        "description": "Invalid product",
        "category": "Testing",
        "price": -1,
        "quantity": 10,
    },
    {
        "name": "Invalid Quantity Negative",
        "description": "Invalid product",
        "category": "Testing",
        "price": 10.99,
        "quantity": -1,
    },
    {
        "name": "Invalid Quantity Float",
        "description": "Invalid product",
        "category": "Testing",
        "price": 10.99,
        "quantity": 1.6,
    },
    {
        "name": 123,
        "description": "Invalid product name",
        "category": "Testing",
        "price": 10.99,
        "quantity": 1,
    },
    {
        "name": "Invalid Description",
        "description": 345,
        "category": "Testing",
        "price": 10.99,
        "quantity": 1,
    },
    {
        "name": "Invalid Category",
        "description": "Invalid Categoey Value",
        "category": 234,
        "price": 10.99,
        "quantity": 1,
    },
    {
        "description": "Missing product name",
        "category": "Testing",
        "price": 10.99,
        "quantity": 5,
    },
    {
        "name": "Missing Category",
        "description": "Missing category",
        "price": 10.99,
        "quantity": 5,
    },
    {
        "name": "Missing Description",
        "category": "Testing",
        "price": 10.99,
        "quantity": 5,
    },
]


INVALID_UPDATE_PRODUCT_PAYLOADS = [
    {"price": 0},
    {"price": -10},
    {"quantity": -1},
    {"description": 2},
    {"quantity":3.4},
    {"name":123},
]

INVALID_SORT_ORDERS = [
    "ascending",
    "descending",
    "up",
    "down",
]

CREATE_PRODUCT_EQUIVALENCE_CASES = [
    # price, quantity, expected_status
    (19.99, 10, 201),    # valid price, valid quantity
    (0, 10, 422),        # zero price
    (-1, 10, 422),       # negative price
    (19.99, -1, 422),    # negative quantity
    (19.99, 1.5, 422),   # float quantity
]


CREATE_PRODUCT_BOUNDARY_CASES = [
    # price, quantity, expected_status
    (0.01, 10, 201),     # minimum valid price
    (0, 10, 422),        # price boundary invalid
    (-0.01, 10, 422),    # just below price boundary
    (-2, 10, 422),       # below price boundary
    (3, 10, 201),        # above valid price boundary

    (10.99, 0, 201),     # minimum valid quantity
    (10.99, -1, 422),    # just quantity boundary
    (10.99, 1, 201),     # just above quantity boundary
    (10.99, -5, 422),    # below quantity boundary
    (10.99, 10, 201),    # above valid quantity boundary
]


UPDATE_PRODUCT_BOUNDARY_CASES = [
    # update_payload, expected_status
    ({"price": 0.01}, 200),
    ({"price": 0}, 422),
    ({"price": -0.01}, 422),

    ({"quantity": 0}, 200),
    ({"quantity": -1}, 422),
    ({"quantity": 1}, 200),
]

PAGINATION_BOUNDARY_CASES = [
    # page, limit, expected_status
    (1, 1, 200),
    (0, 10, 422),
    (-1, 10, 422),
    (1, 0, 422),
    (1, -1, 422),
    (1, 100, 200),
]