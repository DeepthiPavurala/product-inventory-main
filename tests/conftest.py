from __future__ import annotations

import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

import pytest

from tests import config as test_config
from tests.docker_orchestrator import DockerOrchestrator


pytest_plugins = [
    "tests.fixtures.client_fixtures",
]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-docker",
        action="store_true",
        default=False,
        help="Start Docker-backed backend dependencies before running tests.",
    )


def pytest_configure(config: pytest.Config) -> None:
    run_docker = bool(config.getoption("--run-docker"))

    test_config.backend_config = test_config.backend_config.with_docker_enabled(
        run_docker
    )

    if not run_docker:
        return

    orchestrator = DockerOrchestrator(test_config.backend_config)
    orchestrator.start()

    config._docker_orchestrator = orchestrator  # type: ignore[attr-defined]


def pytest_sessionfinish(
    session: pytest.Session,
    exitstatus: int,
) -> None:
    if not session.config.getoption("--run-docker"):
        return

    if test_config.backend_config.keep_containers:
        return

    orchestrator = getattr(
        session.config,
        "_docker_orchestrator",
        None,
    )

    if orchestrator is None:
        orchestrator = DockerOrchestrator(test_config.backend_config)

    orchestrator.stop()