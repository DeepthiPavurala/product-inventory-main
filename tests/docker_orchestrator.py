"""Docker orchestration for pytest using the Python Docker SDK.

The test suite intentionally exposes one Docker-facing class only:
DockerOrchestrator. It owns the Docker SDK client internally, so tests and
pytest hooks do not need a separate DockerClient wrapper or shell commands.
"""

from __future__ import annotations

import time
import urllib.request
from pathlib import Path
from typing import Any

import pytest

from tests.config import BackendTestConfig

try:
    import docker
    from docker.errors import DockerException, NotFound
    from docker.models.containers import Container
except ImportError:
    docker = None  # type: ignore[assignment]
    DockerException = Exception  # type: ignore[assignment]
    NotFound = Exception  # type: ignore[assignment]
    Container = Any  # type: ignore[assignment]


def load_env_file(env_file_path: Path) -> dict[str, str]:
    env_vars: dict[str, str] = {}

    if not env_file_path.exists():
        return env_vars

    for line in env_file_path.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)

        env_vars[key.strip()] = value.strip().strip('"').strip("'")

    return env_vars


class DockerOrchestrator:
    """Single Docker SDK entry point for pytest container lifecycle."""

    def __init__(self, config: BackendTestConfig):
        self.config = config
        self.docker_client: Any | None = None

    def connect(self) -> Any:
        """Create and verify the Docker SDK client."""
        if docker is None:
            pytest.exit(
                "Docker SDK is not installed. Install dev dependencies or run "
                "non-Docker tests without --run-docker."
            )

        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()
            return self.docker_client
        except DockerException as exc:
            pytest.exit(
                "Docker is required for --run-docker tests, but the Docker "
                f"client is unavailable: {exc}"
            )

    def start(self) -> None:
        """Build and start Postgres plus the backend using the Docker SDK."""
        docker_client = self.docker_client or self.connect()
        project_root = Path(__file__).resolve().parents[1]

        network = self._ensure_network(docker_client)

        self._remove_container_if_exists(
            docker_client,
            self.config.backend_container_name,
        )
        self._remove_container_if_exists(
            docker_client,
            self.config.db_container_name,
        )

        db_container = docker_client.containers.run(
            self.config.db_image,
            name=self.config.db_container_name,
            detach=True,
            network=network.name,
            environment={
                "POSTGRES_USER": self.config.db_user,
                "POSTGRES_PASSWORD": self.config.db_password,
                "POSTGRES_DB": self.config.db_name,
            },
            healthcheck={
                "test": ["CMD-SHELL", f"pg_isready -U {self.config.db_user}"],
                "interval": 5_000_000_000,
                "timeout": 5_000_000_000,
                "retries": 5,
            },
            labels={
                "pytest_project": self.config.project_name,
            },
        )

        self._wait_for_postgres(db_container)

        docker_client.images.build(
            path=str(project_root),
            tag=self.config.backend_image,
            rm=True,
        )

        test_env_file = project_root / ".env.test"
        backend_env = load_env_file(test_env_file)

        # Force correct Docker-network database URL for the backend test container.
        # This should override any DATABASE_URL accidentally placed in .env.test.
        backend_env["DATABASE_URL"] = self.config.database_url

        docker_client.containers.run(
            self.config.backend_image,
            name=self.config.backend_container_name,
            detach=True,
            network=network.name,
            environment=backend_env,
            ports={
                f"{self.config.backend_internal_port}/tcp": self.config.backend_host_port
            },
            labels={
                "pytest_project": self.config.project_name,
            },
        )

        self._wait_for_backend()

    def stop(self) -> None:
        """Remove Docker resources created for the pytest session."""
        docker_client = self.docker_client or self.connect()

        for container_name in (
            self.config.backend_container_name,
            self.config.db_container_name,
        ):
            self._remove_container_if_exists(docker_client, container_name)

        try:
            network = docker_client.networks.get(self.config.network_name)
            network.remove()
        except DockerException:
            pass

    def _remove_container_if_exists(
        self,
        docker_client: Any,
        name: str,
    ) -> None:
        try:
            container = docker_client.containers.get(name)
            container.remove(force=True, v=True)
        except NotFound:
            return

    def _ensure_network(self, docker_client: Any) -> Any:
        try:
            return docker_client.networks.get(self.config.network_name)
        except NotFound:
            return docker_client.networks.create(
                self.config.network_name,
                driver="bridge",
            )

    def _wait_for_postgres(self, container: Container) -> None:
        deadline = time.time() + self.config.startup_timeout_seconds

        while time.time() < deadline:
            container.reload()

            health = container.attrs.get("State", {}).get("Health", {}).get("Status")

            if health == "healthy":
                return

            if container.status == "exited":
                logs = container.logs(tail=100).decode("utf-8", errors="replace")
                raise RuntimeError(
                    "Postgres container exited before becoming healthy. "
                    f"Logs:\n{logs}"
                )

            time.sleep(self.config.poll_interval_seconds)

        logs = container.logs(tail=100).decode("utf-8", errors="replace")
        raise RuntimeError(
            "Postgres did not become healthy in time. "
            f"Logs:\n{logs}"
        )

    def _wait_for_backend(self) -> None:
        deadline = time.time() + self.config.startup_timeout_seconds
        health_url = f"{self.config.base_url.rstrip('/')}{self.config.health_path}"

        last_error: Exception | None = None

        while time.time() < deadline:
            try:
                with urllib.request.urlopen(health_url, timeout=5) as response:
                    if 200 <= response.status < 300:
                        return

            except Exception as exc:
                last_error = exc

            time.sleep(self.config.poll_interval_seconds)

        backend_logs = self._get_container_logs(
            self.config.backend_container_name,
            tail=150,
        )

        db_logs = self._get_container_logs(
            self.config.db_container_name,
            tail=80,
        )

        raise RuntimeError(
            f"Backend did not become healthy at {health_url} within "
            f"{self.config.startup_timeout_seconds} seconds.\n"
            f"Last error: {last_error}\n\n"
            f"Backend logs:\n{backend_logs}\n\n"
            f"Database logs:\n{db_logs}"
        )

    def _get_container_logs(
        self,
        container_name: str,
        tail: int = 100,
    ) -> str:
        try:
            docker_client = self.docker_client or self.connect()
            container = docker_client.containers.get(container_name)
            return container.logs(tail=tail).decode("utf-8", errors="replace")

        except Exception as exc:
            return f"Could not fetch logs for {container_name}: {exc}"