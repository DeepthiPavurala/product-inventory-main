"""Centralized test configuration for backend integration and Docker tests."""

from __future__ import annotations

import os
from dataclasses import dataclass, replace

from tests.utils.api_paths import HEALTH_PATH


def _env_bool(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    return raw_value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class BackendTestConfig:
    project_name: str = os.getenv("PYTEST_DOCKER_PROJECT", "product_inventory_tests")
    network_name: str = os.getenv("PYTEST_DOCKER_NETWORK", "product_inventory_tests_net")

    db_image: str = os.getenv("PYTEST_DB_IMAGE", "postgres:15")
    db_container_name: str = os.getenv("PYTEST_DB_CONTAINER", "inventory_test_db")
    db_user: str = os.getenv("TEST_DB_USER", "postgres")
    db_password: str = os.getenv("TEST_DB_PASSWORD", "postgres")
    db_name: str = os.getenv("TEST_DB_NAME", "inventory_test_db")
    db_port: int = int(os.getenv("TEST_DB_PORT", "5432"))

    backend_image: str = os.getenv("PYTEST_BACKEND_IMAGE", "product_inventory_test_backend:latest")
    backend_container_name: str = os.getenv("PYTEST_BACKEND_CONTAINER", "inventory_test_backend")
    backend_internal_port: int = int(os.getenv("TEST_BACKEND_INTERNAL_PORT", "8000"))
    backend_host_port: int = int(os.getenv("TEST_BACKEND_PORT", "8001"))
    base_url: str = os.getenv("TEST_BACKEND_URL", "http://localhost:8001")
    health_path: str = os.getenv("TEST_BACKEND_HEALTH_PATH", HEALTH_PATH)

    startup_timeout_seconds: int = int(os.getenv("TEST_BACKEND_STARTUP_TIMEOUT", "120"))
    poll_interval_seconds: float = float(os.getenv("TEST_BACKEND_POLL_INTERVAL", "2"))

    keep_containers: bool = _env_bool("PYTEST_KEEP_DOCKER", False)
    skip_docker: bool = _env_bool("PYTEST_SKIP_DOCKER", True)

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_container_name}:{self.db_port}/{self.db_name}"
        )

    def with_docker_enabled(self, enabled: bool) -> "BackendTestConfig":
        return replace(self, skip_docker=not enabled)


backend_config = BackendTestConfig()