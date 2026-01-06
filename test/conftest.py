from pathlib import Path

from infrastructure.config.config import CONFIG


def pytest_configure(config):
    CONFIG.update(Path("resources/test-config.yaml"))
