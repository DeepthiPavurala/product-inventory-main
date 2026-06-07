from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import (
    adjust_product_stock,
    create_product,
    get_product_by_id,
    get_products,
    soft_delete_product,
    update_product,
)


def unique_product_payload(
    name_prefix: str = "Integration Product",
    description: str = "Integration test product",
    category: str = "Electronics",
    price: float = 99.99,
    quantity: int = 10,
) -> dict:
    return {
        "name": f"{name_prefix}-{uuid.uuid4().hex[:8]}",
        "description": description,
        "category": category,
        "price": price,
        "quantity": quantity,
    }


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(autouse=True)
def mock_low_stock_email(monkeypatch):
    sent_quantities = []

    def fake_notify(product):
        sent_quantities.append(product.quantity)
        return product.quantity <= 5

    monkeypatch.setattr(
        "app.services.product_service.notify_if_low_stock",
        fake_notify,
    )

    return sent_quantities


@pytest.mark.integration
def test_create_product_persists_product_and_can_fetch_by_id(
    db_session,
    mock_low_stock_email,
):
    payload = ProductCreate(
        **unique_product_payload(
            name_prefix="Persisted Product",
            quantity=8,
        )
    )

    product = create_product(db_session, payload)

    fetched_product = get_product_by_id(db_session, product.id)

    assert product.id is not None
    assert fetched_product is not None
    assert fetched_product.id == product.id
    assert fetched_product.name == payload.name
    assert fetched_product.description == payload.description
    assert fetched_product.category == payload.category
    assert float(fetched_product.price) == payload.price
    assert fetched_product.quantity == payload.quantity
    assert fetched_product.is_active is True

    assert mock_low_stock_email == [8]


@pytest.mark.integration
@pytest.mark.negative
def test_create_product_duplicate_name_raises_exception(db_session):
    payload = ProductCreate(
        **unique_product_payload(
            name_prefix="Duplicate DB Product",
        )
    )

    create_product(db_session, payload)

    with pytest.raises(Exception, match="Product name must be unique"):
        create_product(db_session, payload)


@pytest.mark.integration
def test_get_products_returns_paginated_active_products(db_session):
    category = f"DB Pagination-{uuid.uuid4().hex[:8]}"

    for index in range(7):
        create_product(
            db_session,
            ProductCreate(
                **unique_product_payload(
                    name_prefix=f"DB Paginated Product {index}",
                    category=category,
                    quantity=10,
                )
            ),
        )

    result = get_products(
        db_session,
        page=1,
        limit=5,
        category=category,
        sort_by="created_at",
        sort_order="asc",
    )

    assert result["total"] == 7
    assert result["page"] == 1
    assert result["limit"] == 5
    assert result["total_pages"] == 2
    assert len(result["data"]) == 5

    for product in result["data"]:
        assert product.category == category
        assert product.is_active is True


@pytest.mark.integration
def test_get_products_search_by_name_returns_matching_product(db_session):
    payload = ProductCreate(
        **unique_product_payload(
            name_prefix="Search DB Product",
            category="Search Category",
        )
    )

    created_product = create_product(db_session, payload)

    result = get_products(
        db_session,
        page=1,
        limit=10,
        search=created_product.name,
        sort_by="created_at",
        sort_order="asc",
    )

    assert result["total"] == 1
    assert result["data"][0].id == created_product.id
    assert result["data"][0].name == created_product.name


@pytest.mark.integration
def test_update_product_persists_changes(db_session):
    product = create_product(
        db_session,
        ProductCreate(
            **unique_product_payload(
                name_prefix="DB Update Target",
                price=99.99,
                quantity=10,
            )
        ),
    )

    update_payload = ProductUpdate(
        name=f"Updated DB Product-{uuid.uuid4().hex[:8]}",
        description="Updated integration description",
        category="Updated DB Category",
        price=199.99,
        quantity=25,
    )

    updated_product = update_product(
        db_session,
        product.id,
        update_payload,
    )

    fetched_product = get_product_by_id(db_session, product.id)

    assert updated_product is not None
    assert fetched_product is not None
    assert fetched_product.id == product.id
    assert fetched_product.name == update_payload.name
    assert fetched_product.description == update_payload.description
    assert fetched_product.category == update_payload.category
    assert float(fetched_product.price) == update_payload.price
    assert fetched_product.quantity == update_payload.quantity


@pytest.mark.integration
def test_update_product_partial_price_persists_change(db_session):
    product = create_product(
        db_session,
        ProductCreate(
            **unique_product_payload(
                name_prefix="DB Partial Update",
                price=99.99,
                quantity=10,
            )
        ),
    )

    update_payload = ProductUpdate(price=149.99)

    updated_product = update_product(
        db_session,
        product.id,
        update_payload,
    )

    fetched_product = get_product_by_id(db_session, product.id)

    assert updated_product is not None
    assert fetched_product is not None
    assert float(fetched_product.price) == 149.99
    assert fetched_product.name == product.name
    assert fetched_product.quantity == 10


@pytest.mark.integration
@pytest.mark.negative
def test_update_product_invalid_id_returns_none(db_session):
    update_payload = ProductUpdate(
        name="Does Not Exist",
        description="Invalid update",
        category="Invalid",
        price=10.99,
        quantity=1,
    )

    updated_product = update_product(
        db_session,
        str(uuid.uuid4()),
        update_payload,
    )

    assert updated_product is None


@pytest.mark.integration
def test_adjust_stock_adds_quantity_and_persists(db_session):
    product = create_product(
        db_session,
        ProductCreate(
            **unique_product_payload(
                name_prefix="DB Stock Add",
                quantity=10,
            )
        ),
    )

    updated_product, alert_sent = adjust_product_stock(
        db_session,
        product.id,
        delta=5,
    )

    fetched_product = get_product_by_id(db_session, product.id)

    assert updated_product is not None
    assert fetched_product is not None
    assert updated_product.id == product.id
    assert fetched_product.quantity == 15
    assert alert_sent is False


@pytest.mark.integration
def test_adjust_stock_reduces_quantity_and_sends_low_stock_alert(
    db_session,
    mock_low_stock_email,
):
    product = create_product(
        db_session,
        ProductCreate(
            **unique_product_payload(
                name_prefix="DB Stock Reduce",
                quantity=10,
            )
        ),
    )

    updated_product, alert_sent = adjust_product_stock(
        db_session,
        product.id,
        delta=-8,
    )

    fetched_product = get_product_by_id(db_session, product.id)

    assert updated_product is not None
    assert fetched_product is not None
    assert fetched_product.quantity == 2
    assert alert_sent is True

    assert 2 in mock_low_stock_email


@pytest.mark.integration
@pytest.mark.negative
def test_adjust_stock_rejects_negative_inventory(db_session):
    product = create_product(
        db_session,
        ProductCreate(
            **unique_product_payload(
                name_prefix="DB Negative Stock",
                quantity=2,
            )
        ),
    )

    with pytest.raises(ValueError, match="cannot be negative"):
        adjust_product_stock(
            db_session,
            product.id,
            delta=-3,
        )


@pytest.mark.integration
@pytest.mark.negative
def test_adjust_stock_invalid_id_returns_none_and_false(db_session):
    updated_product, alert_sent = adjust_product_stock(
        db_session,
        str(uuid.uuid4()),
        delta=5,
    )

    assert updated_product is None
    assert alert_sent is False


@pytest.mark.integration
def test_soft_delete_product_marks_inactive_and_hides_from_get_by_id(db_session):
    product = create_product(
        db_session,
        ProductCreate(
            **unique_product_payload(
                name_prefix="DB Soft Delete",
            )
        ),
    )

    deleted_product = soft_delete_product(db_session, product.id)

    fetched_product = get_product_by_id(db_session, product.id)

    assert deleted_product is not None
    assert deleted_product.id == product.id
    assert deleted_product.is_active is False
    assert fetched_product is None


@pytest.mark.integration
@pytest.mark.negative
def test_soft_delete_product_invalid_id_returns_none(db_session):
    deleted_product = soft_delete_product(
        db_session,
        str(uuid.uuid4()),
    )

    assert deleted_product is None


@pytest.mark.integration
def test_soft_deleted_product_not_returned_in_product_list(db_session):
    active_product = create_product(
        db_session,
        ProductCreate(
            **unique_product_payload(
                name_prefix="DB Active Product",
                category="Soft Delete List Category",
            )
        ),
    )

    deleted_product = create_product(
        db_session,
        ProductCreate(
            **unique_product_payload(
                name_prefix="DB Deleted Product",
                category="Soft Delete List Category",
            )
        ),
    )

    soft_delete_product(db_session, deleted_product.id)

    result = get_products(
        db_session,
        page=1,
        limit=10,
        category="Soft Delete List Category",
        sort_by="created_at",
        sort_order="asc",
    )

    returned_ids = [product.id for product in result["data"]]

    assert active_product.id in returned_ids
    assert deleted_product.id not in returned_ids
    assert result["total"] == 1