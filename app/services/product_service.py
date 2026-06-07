from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, asc, desc
from app.core.exceptions import ProductAlreadyExistsException
from app.models.product import Product
from app.services.email_service import notify_if_low_stock
import logging

logger = logging.getLogger(__name__)


def create_product(db: Session, product_data):
    logger.info(f'Attempting to create product: {product_data.name}')
    existing = db.query(Product).filter(
        Product.name == product_data.name,
        Product.is_active == True
    ).first()

    if existing:
        logger.warning(f"Duplicate product name attempted: {product_data.name}")
        raise ProductAlreadyExistsException("Product name must be unique")
    
    product = Product(**product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    notify_if_low_stock(product)
    logger.info(f"Product created successfully: {product.id}")
    return product

def get_products(
    db,
    page: int = 1,
    limit: int = 5,
    search: str = None,
    category: str = None,
    sort_by: str = "created_at",
    sort_order: str = "asc"
):
    logger.info(
        f"Fetching products | page={page} | search={search} | "
        f"category={category} | sort_by={sort_by} | order={sort_order}"
    )
    query = select(Product).where(Product.is_active == True)

    # Search
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Product.id.ilike(search_term),
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.category.ilike(search_term),
            )
        )
    if category:
        query = query.where(Product.category == category)
        
    # Sorting
    allowed_sort_fields = {
        "id": Product.id,
        "name": Product.name,
        "category": Product.category,
        "price": Product.price,
        "quantity": Product.quantity,
        "created_at": Product.created_at,
    }

    sort_column = allowed_sort_fields.get(sort_by, Product.created_at)

    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    # Count total
    total_query = select(func.count()).select_from(query.subquery())
    total = db.execute(total_query).scalar()

    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    results = db.execute(query).scalars().all()

    logger.info(
        f"Products fetched successfully | total={total} | page ={page} | limit={limit}"
        )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "data": results
    }

def update_product(db: Session, product_id: str, product_data):
    logger.info(f"Updating product with ID: {product_id}")
    product = get_product_by_id(db, product_id)
    if not product or product.is_active is False:
        logger.warning(f"Update failed — product not found or inactive| ID: {product_id}")
        return None
    update_data = product_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    low_stock_alert_sent = notify_if_low_stock(product)

    logger.info(
        f"Product updated successfully | id={product_id} | low_stock_alert_sent={low_stock_alert_sent}",
    )

    return product

def get_product_by_id(db: Session, product_id: str):
    """Return one active product by ID, or None when not found."""
    logger.info("Fetching product by ID | id=%s", product_id)

    product = db.get(Product, product_id)

    if not product:
        logger.warning("Product not found | id=%s", product_id)
        return None

    if product.is_active is False:
        logger.warning("Product is inactive | id=%s", product_id)
        return None

    return product

def adjust_product_stock(db: Session, product_id: str, delta: int):
    """Adjust stock by delta and send a low-stock alert when threshold is reached.

    Raises ValueError when the adjustment would make inventory negative.
    Returns a tuple of (product, low_stock_alert_sent).
    """
    logger.info(
        f"Adjusting product stock | id={product_id} | delta={delta}",
    )

    product = get_product_by_id(db, product_id)

    if not product:
        logger.warning("Stock adjustment failed - product not found or inactive | id=%s", product_id)
        return None, False

    new_quantity = product.quantity + delta

    if new_quantity < 0:
        logger.warning(
            f"Stock adjustment rejected - negative inventory | id={product_id} | current_quantity={product.quantity} | delta={delta}",
        )
        raise ValueError("Stock quantity cannot be negative")

    product.quantity = new_quantity

    db.commit()
    db.refresh(product)

    low_stock_alert_sent = notify_if_low_stock(product)

    logger.info(
        "Stock adjusted successfully | id=%s | new_quantity=%s | low_stock_alert_sent=%s",
        product_id,
        product.quantity,
        low_stock_alert_sent,
    )

    return product, low_stock_alert_sent


def soft_delete_product(db: Session, product_id: str):
    logger.info(f"Deleting product | ID: {product_id}")
    product = get_product_by_id(db, product_id)
    if not product:
        logger.warning(f"Delete failed — product not found | ID: {product_id}")
        return None

    product.is_active = False
    db.commit()
    db.refresh(product)

    logger.info(f"Product soft deleted | ID: {product_id}")

    return product