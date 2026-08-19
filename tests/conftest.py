import os

import pytest
from dotenv import load_dotenv

from pylegifrance.client import LegifranceClient
from pylegifrance.config import ApiConfig

load_dotenv()


def credentials_available() -> bool:
    """Check whether Legifrance API credentials are configured."""
    return bool(
        os.getenv("LEGIFRANCE_CLIENT_ID") and os.getenv("LEGIFRANCE_CLIENT_SECRET")
    )


requires_credentials = pytest.mark.skipif(
    not credentials_available(),
    reason="Legifrance credentials not configured (fork PRs run without secrets)",
)


@pytest.fixture(scope="module")
def api_client() -> LegifranceClient:
    """Create a real Legifrance client for integration tests."""
    if not credentials_available():
        pytest.skip(
            "Legifrance credentials not configured (fork PRs run without secrets)"
        )
    config = ApiConfig.from_env()
    return LegifranceClient(config=config)
