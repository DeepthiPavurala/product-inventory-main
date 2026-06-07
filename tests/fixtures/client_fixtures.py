from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import product as product_routes
from app.db.base import Base
from app.main import app
from app.models.product import Product
from tests import config as test_config
from tests.fakeapi.request_client import ApiResponse, RequestClient


class InProcessRequestClient:
    """
    Adapter around FastAPI TestClient.

    It exposes the same interface used by ProductInventory:
    get/post/patch/delete returning ApiResponse.
    """

    def __init__(self, test_client: TestClient) -> None:
        self.test_client = test_client

    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        response_model: type | Any | None = None,
    ):
        response = self.test_client.get(path, params=params)

        return ApiResponse(
            status_code=response.status_code,
            body=response.content,
            response_model=response_model,
        )

    def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        response_model: type | Any | None = None,
    ):
        response = self.test_client.post(path, json=json)

        return ApiResponse(
            status_code=response.status_code,
            body=response.content,
            response_model=response_model,
        )

    def patch(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        response_model: type | Any | None = None,
    ):
        response = self.test_client.patch(path, json=json)

        return ApiResponse(
            status_code=response.status_code,
            body=response.content,
            response_model=response_model,
        )

    def delete(
        self,
        path: str,
        response_model: type | Any | None = None,
    ):
        response = self.test_client.delete(path)

        return ApiResponse(
            status_code=response.status_code,
            body=response.content,
            response_model=response_model,
        )

@pytest.fixture(scope="session")
def client(request):
    run_docker = bool(request.config.getoption("--run-docker"))

    if run_docker:
        yield RequestClient(test_config.backend_config.base_url)
        return

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

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[product_routes.get_db] = override_get_db

    with TestClient(app) as test_client:
        yield InProcessRequestClient(test_client)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()