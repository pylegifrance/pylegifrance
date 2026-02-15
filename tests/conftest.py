import pytest

from pylegifrance.client import LegifranceClient
from pylegifrance.config import ApiConfig


@pytest.fixture(scope="module")
def api_client() -> LegifranceClient:
    """Create a real Legifrance client for integration tests."""
    config = ApiConfig.from_env()
    return LegifranceClient(config=config)
