from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.payment import router as payment_router
from app.api.routes.product import router as product_router
from app.core.api_paths import API_PREFIX, HEALTH_PATH, ROOT_PATH, api_routes
from app.core.exception_handlers import register_exception_handlers
from app.core.logging_config import setup_logging
from app.core.request_logging import RequestLoggingMiddleware
from app.db.base import Base
from app.db.session import engine


setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Product Inventory API")

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")

    yield

    logger.info("Stopping Product Inventory API")


app = FastAPI(
    title="Product Inventory API",
    version="0.1.0",
    lifespan=lifespan,
)


origins = [
    "http://localhost:3000",
]


app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


register_exception_handlers(app)


@app.get(HEALTH_PATH, tags=["System"])
def health():
    logger.info("Health check called")
    return {"status": "healthy"}


@app.get(ROOT_PATH, include_in_schema=False)
def root():
    logger.info("Root endpoint called")
    return {
        "message": "Product Inventory API is running",
        "docs": "/docs",
        "health": api_routes.health,
        "api_base": api_routes.api_root,
        "products": api_routes.products,
        "payments": api_routes.payments,
    }


@app.get(API_PREFIX, include_in_schema=False)
def api_root():
    logger.info("API root endpoint called")
    return {
        "message": "Product Inventory API v1",
        "available_endpoints": {
            "products": api_routes.products,
            "categories": api_routes.product_categories,
            "payments": api_routes.payments,
            "checkout": api_routes.payment_checkout,
            "health": api_routes.health,
        },
    }


app.include_router(product_router, prefix=API_PREFIX)
app.include_router(payment_router, prefix=API_PREFIX)