from __future__ import annotations

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import ProductAlreadyExistsException
from app.services import product_service
from tests.data.product_payloads import (
    create_product_request_data,
    partial_update_price_request_data,
    partial_update_quantity_request_data,
    update_product_request_data,
)
from tests.mocks.email_mocks import EmailMock


def fake_product(
    product_id: str | None = None,
    name: str = "Mock Product",
    description: str = "Mock product description",
    category: str = "Electronics",
    price: float = 99.99,
    quantity: int = 10,
    is_active: bool = True,
):
    return SimpleNamespace(
        id=product_id or str(uuid.uuid4()),
        name=name,
        description=description,
        category=category,
        price=price,
        quantity=quantity,
        is_active=is_active,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def mock_query_first(db: MagicMock, return_value):
    """
    Mocks:
        db.query(...).filter(...).first()

    Used by create_product duplicate-name check.
    """
    query_mock = MagicMock()
    filter_mock = MagicMock()

    db.query.return_value = query_mock
    query_mock.filter.return_value = filter_mock
    filter_mock.first.return_value = return_value

    return filter_mock


def mock_execute_scalar(return_value):
    """
    Mocks:
        db.execute(...).scalar()
    """
    execute_result = MagicMock()
    execute_result.scalar.return_value = return_value
    return execute_result


def mock_execute_scalars_all(return_value):
    """
    Mocks:
        db.execute(...).scalars().all()
    """
    execute_result = MagicMock()
    execute_result.scalars.return_value.all.return_value = return_value
    return execute_result

@pytest.mark.unit
@pytest.mark.negative
def test_create_product_commit_failure_raises(monkeypatch):
    db = MagicMock()

    mock_query_first(db, None)
    db.commit.side_effect = Exception("DB commit failed")

    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        lambda product: False,
    )

    payload = create_product_request_data(
        name_prefix="Commit Failure Product",
    )

    with pytest.raises(Exception, match="DB commit failed"):
        product_service.create_product(db, payload)

    db.add.assert_called_once()
    db.commit.assert_called_once()

@pytest.mark.unit
def test_create_product_valid_mocks_db_and_email(monkeypatch):
    db = MagicMock()

    # create_product checks duplicate product using db.query(...).filter(...).first()
    mock_query_first(db, None)

    email_mock = EmailMock(return_value=False)
    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        email_mock.notify_if_low_stock,
    )

    payload = create_product_request_data(
        name_prefix="Unit Create Product",
        price=99.99,
        quantity=10,
    )

    product = product_service.create_product(db, payload)

    assert product is not None
    assert product.name == payload.name
    assert product.description == payload.description
    assert product.category == payload.category
    assert product.price == payload.price
    assert product.quantity == payload.quantity

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


@pytest.mark.unit
@pytest.mark.negative
def test_create_product_duplicate_raises_exception(monkeypatch):
    db = MagicMock()

    existing_product = fake_product(name="Duplicate Product")
    mock_query_first(db, existing_product)

    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        lambda product: False,
    )

    payload = create_product_request_data(
        name_prefix="Duplicate Product",
    )

    with pytest.raises(ProductAlreadyExistsException):
        product_service.create_product(db, payload)

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


@pytest.mark.unit
def test_create_product_low_stock_email_called(monkeypatch):
    db = MagicMock()

    mock_query_first(db, None)

    email_mock = EmailMock(return_value=True)
    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        email_mock.notify_if_low_stock,
    )

    payload = create_product_request_data(
        name_prefix="Low Stock Unit Product",
        quantity=1,
    )

    product = product_service.create_product(db, payload)

    assert product is not None
    assert product.quantity == 1
    assert email_mock.was_called_once()
    assert email_mock.calls[0].name == product.name

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


@pytest.mark.unit
def test_get_product_by_id_valid():
    db = MagicMock()

    product = fake_product(is_active=True)
    db.get.return_value = product

    result = product_service.get_product_by_id(db, product.id)

    assert result is not None
    assert result.id == product.id
    assert result.name == product.name
    assert result.is_active is True

    db.get.assert_called_once()


@pytest.mark.unit
@pytest.mark.negative
def test_get_product_by_id_invalid_returns_none():
    db = MagicMock()

    db.get.return_value = None

    result = product_service.get_product_by_id(db, str(uuid.uuid4()))

    assert result is None
    db.get.assert_called_once()


@pytest.mark.unit
@pytest.mark.negative
def test_get_product_by_id_inactive_returns_none():
    db = MagicMock()

    product = fake_product(is_active=False)
    db.get.return_value = product

    result = product_service.get_product_by_id(db, product.id)

    assert result is None
    db.get.assert_called_once()


@pytest.mark.unit
def test_get_products_paginated_mocks_count_and_data():
    db = MagicMock()

    products = [
        fake_product(name="Product 1", category="Electronics"),
        fake_product(name="Product 2", category="Electronics"),
    ]

    db.execute.side_effect = [
        mock_execute_scalar(2),
        mock_execute_scalars_all(products),
    ]

    result = product_service.get_products(
        db,
        page=1,
        limit=5,
        category="Electronics",
        sort_by="created_at",
        sort_order="asc",
    )

    assert result["total"] == 2
    assert result["page"] == 1
    assert result["limit"] == 5
    assert result["total_pages"] == 1
    assert result["data"] == products

    assert db.execute.call_count == 2


@pytest.mark.unit
def test_get_products_empty_result():
    db = MagicMock()

    db.execute.side_effect = [
        mock_execute_scalar(0),
        mock_execute_scalars_all([]),
    ]

    result = product_service.get_products(
        db,
        page=1,
        limit=5,
        search="NoSuchProduct",
        sort_by="created_at",
        sort_order="asc",
    )

    assert result["total"] == 0
    assert result["page"] == 1
    assert result["limit"] == 5
    assert result["total_pages"] == 0
    assert result["data"] == []

    assert db.execute.call_count == 2


@pytest.mark.unit
@pytest.mark.parametrize("sort_order", ["asc", "desc"])
def test_get_products_valid_sort_orders(sort_order):
    db = MagicMock()

    products = [
        fake_product(name="Sort Product 1", price=10.00),
        fake_product(name="Sort Product 2", price=20.00),
    ]

    db.execute.side_effect = [
        mock_execute_scalar(2),
        mock_execute_scalars_all(products),
    ]

    result = product_service.get_products(
        db,
        page=1,
        limit=10,
        sort_by="price",
        sort_order=sort_order,
    )

    assert result["total"] == 2
    assert result["data"] == products
    assert db.execute.call_count == 2


@pytest.mark.unit
@pytest.mark.negative
def test_update_product_commit_failure_raises(monkeypatch):
    db = MagicMock()

    product = fake_product(quantity=10)
    db.get.return_value = product
    db.commit.side_effect = Exception("DB commit failed")

    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        lambda product: False,
    )

    update_payload = partial_update_quantity_request_data(quantity=5)

    with pytest.raises(Exception, match="DB commit failed"):
        product_service.update_product(
            db,
            product.id,
            update_payload,
        )

    db.commit.assert_called_once()

@pytest.mark.unit
def test_update_product_valid_mocks_db_and_email(monkeypatch):
    db = MagicMock()

    existing_product = fake_product(
        name="Original Product",
        price=99.99,
        quantity=10,
        is_active=True,
    )

    db.get.return_value = existing_product

    email_mock = EmailMock(return_value=False)
    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        email_mock.notify_if_low_stock,
    )

    update_payload = update_product_request_data(
        name_prefix="Updated Unit Product",
        category="Updated Category",
        price=199.99,
        quantity=25,
    )

    updated_product = product_service.update_product(
        db,
        existing_product.id,
        update_payload,
    )

    assert updated_product is not None
    assert updated_product.id == existing_product.id
    assert updated_product.name == update_payload.name
    assert updated_product.description == update_payload.description
    assert updated_product.category == update_payload.category
    assert updated_product.price == update_payload.price
    assert updated_product.quantity == update_payload.quantity

    db.commit.assert_called_once()
    db.refresh.assert_called_once()


@pytest.mark.unit
def test_update_product_partial_price_valid(monkeypatch):
    db = MagicMock()

    existing_product = fake_product(
        name="Partial Update Product",
        price=99.99,
        quantity=10,
        is_active=True,
    )

    db.get.return_value = existing_product

    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        lambda product: False,
    )

    update_payload = partial_update_price_request_data(price=149.99)

    updated_product = product_service.update_product(
        db,
        existing_product.id,
        update_payload,
    )

    assert updated_product is not None
    assert updated_product.id == existing_product.id
    assert updated_product.price == 149.99
    assert updated_product.name == "Partial Update Product"
    assert updated_product.quantity == 10

    db.commit.assert_called_once()
    db.refresh.assert_called_once()


@pytest.mark.unit
def test_update_product_partial_quantity_valid(monkeypatch):
    db = MagicMock()

    existing_product = fake_product(
        name="Partial Quantity Product",
        price=99.99,
        quantity=10,
        is_active=True,
    )

    db.get.return_value = existing_product

    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        lambda product: False,
    )

    update_payload = partial_update_quantity_request_data(quantity=3)

    updated_product = product_service.update_product(
        db,
        existing_product.id,
        update_payload,
    )

    assert updated_product is not None
    assert updated_product.quantity == 3
    assert updated_product.price == 99.99
    assert updated_product.name == "Partial Quantity Product"

    db.commit.assert_called_once()
    db.refresh.assert_called_once()


@pytest.mark.unit
@pytest.mark.negative
def test_update_product_invalid_id_returns_none():
    db = MagicMock()

    db.get.return_value = None

    update_payload = update_product_request_data(
        name_prefix="Invalid Update Product",
    )

    updated_product = product_service.update_product(
        db,
        str(uuid.uuid4()),
        update_payload,
    )

    assert updated_product is None
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


@pytest.mark.unit
@pytest.mark.negative
def test_update_product_inactive_product_returns_none():
    db = MagicMock()

    inactive_product = fake_product(is_active=False)
    db.get.return_value = inactive_product

    update_payload = update_product_request_data(
        name_prefix="Inactive Product Update",
    )

    updated_product = product_service.update_product(
        db,
        inactive_product.id,
        update_payload,
    )

    assert updated_product is None
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


@pytest.mark.unit
def test_update_product_low_stock_email_called(monkeypatch):
    db = MagicMock()

    existing_product = fake_product(
        name="Update Low Stock Product",
        quantity=10,
        is_active=True,
    )

    db.get.return_value = existing_product

    email_mock = EmailMock(return_value=True)
    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        email_mock.notify_if_low_stock,
    )

    update_payload = partial_update_quantity_request_data(quantity=1)

    updated_product = product_service.update_product(
        db,
        existing_product.id,
        update_payload,
    )

    assert updated_product is not None
    assert updated_product.quantity == 1
    assert email_mock.was_called_once()

    db.commit.assert_called_once()
    db.refresh.assert_called_once()

@pytest.mark.unit
@pytest.mark.negative
def test_soft_delete_product_commit_failure_raises():
    db = MagicMock()

    product = fake_product(is_active=True)
    db.get.return_value = product
    db.commit.side_effect = Exception("DB commit failed")

    with pytest.raises(Exception, match="DB commit failed"):
        product_service.soft_delete_product(
            db,
            product.id,
        )

    db.commit.assert_called_once()

@pytest.mark.unit
def test_soft_delete_product_valid():
    db = MagicMock()

    product = fake_product(is_active=True)
    db.get.return_value = product

    deleted_product = product_service.soft_delete_product(
        db,
        product.id,
    )

    assert deleted_product is not None
    assert deleted_product.id == product.id
    assert deleted_product.is_active is False

    db.commit.assert_called_once()
    db.refresh.assert_called_once()


@pytest.mark.unit
@pytest.mark.negative
def test_soft_delete_product_invalid_id_returns_none():
    db = MagicMock()

    db.get.return_value = None

    deleted_product = product_service.soft_delete_product(
        db,
        str(uuid.uuid4()),
    )

    assert deleted_product is None
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


@pytest.mark.unit
@pytest.mark.negative
def test_soft_delete_product_inactive_product_returns_none():
    db = MagicMock()

    inactive_product = fake_product(is_active=False)
    db.get.return_value = inactive_product

    deleted_product = product_service.soft_delete_product(
        db,
        inactive_product.id,
    )

    assert deleted_product is None
    db.commit.assert_not_called()
    db.refresh.assert_not_called()

@pytest.mark.unit
@pytest.mark.negative
def test_adjust_stock_commit_failure_raises(monkeypatch):
    db = MagicMock()

    product = fake_product(quantity=10)
    db.get.return_value = product
    db.commit.side_effect = Exception("DB commit failed")

    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        lambda product: False,
    )

    with pytest.raises(Exception, match="DB commit failed"):
        product_service.adjust_product_stock(
            db,
            product.id,
            delta=-2,
        )

    db.commit.assert_called_once()

@pytest.mark.unit
def test_adjust_product_stock_adds_quantity(monkeypatch):
    db = MagicMock()

    product = fake_product(quantity=10, is_active=True)
    db.get.return_value = product

    email_mock = EmailMock(return_value=False)
    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        email_mock.notify_if_low_stock,
    )

    updated_product, alert_sent = product_service.adjust_product_stock(
        db,
        product.id,
        delta=5,
    )

    assert updated_product is not None
    assert updated_product.id == product.id
    assert updated_product.quantity == 15
    assert alert_sent is False

    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert email_mock.was_called_once()


@pytest.mark.unit
def test_adjust_product_stock_reduces_quantity_and_sends_alert(monkeypatch):
    db = MagicMock()

    product = fake_product(quantity=10, is_active=True)
    db.get.return_value = product

    email_mock = EmailMock(return_value=True)
    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        email_mock.notify_if_low_stock,
    )

    updated_product, alert_sent = product_service.adjust_product_stock(
        db,
        product.id,
        delta=-8,
    )

    assert updated_product is not None
    assert updated_product.quantity == 2
    assert alert_sent is True
    assert email_mock.was_called_once()

    db.commit.assert_called_once()
    db.refresh.assert_called_once()


@pytest.mark.unit
@pytest.mark.negative
def test_adjust_product_stock_invalid_negative_result_raises_error(monkeypatch):
    db = MagicMock()

    product = fake_product(quantity=5, is_active=True)
    db.get.return_value = product

    monkeypatch.setattr(
        product_service,
        "notify_if_low_stock",
        lambda product: False,
    )

    with pytest.raises(ValueError, match="Stock quantity cannot be negative"):
        product_service.adjust_product_stock(
            db,
            product.id,
            delta=-6,
        )

    db.commit.assert_not_called()
    db.refresh.assert_not_called()


@pytest.mark.unit
@pytest.mark.negative
def test_adjust_product_stock_invalid_id_returns_none_and_false():
    db = MagicMock()

    db.get.return_value = None

    updated_product, alert_sent = product_service.adjust_product_stock(
        db,
        str(uuid.uuid4()),
        delta=5,
    )

    assert updated_product is None
    assert alert_sent is False

    db.commit.assert_not_called()
    db.refresh.assert_not_called()


@pytest.mark.unit
@pytest.mark.negative
def test_adjust_product_stock_inactive_product_returns_none_and_false():
    db = MagicMock()

    inactive_product = fake_product(is_active=False)
    db.get.return_value = inactive_product

    updated_product, alert_sent = product_service.adjust_product_stock(
        db,
        inactive_product.id,
        delta=5,
    )

    assert updated_product is None
    assert alert_sent is False

    db.commit.assert_not_called()
    db.refresh.assert_not_called()