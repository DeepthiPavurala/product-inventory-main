from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.core.exceptions import ProductAlreadyExistsException
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from app.db.session import SessionLocal
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate, ProductDeleteResponse, StockAdjustment, StockResponse
from app.services.product_service import *
from app.core.api_paths import PRODUCTS_PREFIX, PRODUCT_CATEGORIES_PATH
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix=PRODUCTS_PREFIX, tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(PRODUCT_CATEGORIES_PATH)
def get_unique_categories(db: Session = Depends(get_db)):
    logger.info("Fetching unique categories by calling GET /products/categories")
    categories = (
        db.query(distinct(Product.category))
        .filter(Product.category.isnot(None))
        .all()
    )

    logger.info(f"Categories fetched | count={len(categories)}")

    # categories comes as list of tuples [('Electronics',), ('Gaming',)]
    return [c[0] for c in categories]

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="Create Product")
def create(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        logger.info("POST /products called")
        return create_product(db, product)
    except ProductAlreadyExistsException:
        raise HTTPException(
            status_code=400,
            detail="Product name already exists"
        )

@router.get("")
def list_products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1),
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    sort_by: str = "created_at",
    sort_order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db),
):
    logger.info(
        "GET /products called | page=%s | limit=%s | search=%s | category=%s | sort_by=%s | sort_order=%s",
        page,
        limit,
        search,
        category,
        sort_by,
        sort_order,
    )

    return get_products(
        db,
        page=page,
        limit=limit,
        search=search,
        category=category,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{product_id}", response_model=ProductResponse, summary="Get Product")
def get_product(product_id: str, db: Session = Depends(get_db)):
    logger.info("GET /products/{product_id} called")
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.patch("/{product_id}/stock", response_model=StockResponse, summary="Adjust Stock")
def adjust_stock(product_id: str, payload: StockAdjustment, db: Session = Depends(get_db)):
    logger.info("PATCH /products/{product_id}/stock called")
    try:
        product, alert_sent = adjust_product_stock(db, product_id, payload.delta)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return StockResponse(
        id=product.id,
        name=product.name,
        quantity=product.quantity,
        low_stock_alert_sent=alert_sent,
    )

@router.patch("/{product_id}", response_model=ProductResponse, summary="Update Product")
def update(product_id: str, product: ProductUpdate, db: Session = Depends(get_db)):
    logger.info("PATCH /products/{product_id} called")
    updated = update_product(db, product_id, product)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return updated


@router.delete("/{product_id}", response_model=ProductDeleteResponse, summary="Delete Product")
def delete(product_id: str, db: Session = Depends(get_db)):
    logger.info("DELETE /products/{product_id} called")
    deleted = soft_delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return {"message": "Product deleted"}