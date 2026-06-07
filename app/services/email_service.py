"""Email notification service for inventory events."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.models.product import Product

logger = logging.getLogger(__name__)


def should_send_low_stock_alert(quantity: int, threshold: int | None = None) -> bool:
    """Return True when inventory quantity is at or below the alert threshold."""
    effective_threshold = settings.LOW_STOCK_THRESHOLD if threshold is None else threshold
    return quantity <= effective_threshold


def build_low_stock_email(product: Product) -> EmailMessage:
    """Build a low-stock alert email for a product."""
    message = EmailMessage()
    message["Subject"] = f"Low stock alert: {product.name}"
    message["From"] = settings.LOW_STOCK_ALERT_FROM
    message["To"] = settings.LOW_STOCK_ALERT_TO
    message.set_content(
        f"Product '{product.name}' is low in stock. Current quantity: {product.quantity}."
    )
    return message


def send_low_stock_email(product: Product) -> None:
    """Send a low-stock alert email through SMTP."""
    email_message = build_low_stock_email(product)
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.send_message(email_message)
    logger.info("Low-stock alert email sent | product_id=%s | quantity=%s", product.id, product.quantity)


def notify_if_low_stock(product) -> bool:
    if not should_send_low_stock_alert(product.quantity):
        return False

    try:
        send_low_stock_email(product)
        return True
    except Exception as exc:
        logger.warning("Low-stock email notification failed: %s", exc)
        return False
