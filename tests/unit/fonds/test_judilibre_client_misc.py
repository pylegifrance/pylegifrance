"""Unit tests for JudilibreClient error handling and close(), not covered by
test_judilibre_client.py / test_judilibre_client_retry.py. Only the
requests.Session / AuthenticationManager boundary is mocked.
"""

from unittest.mock import MagicMock, patch

import pytest

from pylegifrance.client import _TransientAPIError
from pylegifrance.config import PROD_API_URL, SANDBOX_API_URL, ApiConfig
from pylegifrance.fonds.judilibre import (
    JUDILIBRE_PROD_URL,
    JUDILIBRE_SANDBOX_URL,
    JudilibreAPIError,
    JudilibreClient,
)


def _client() -> JudilibreClient:
    client = JudilibreClient(
        config=ApiConfig(client_id="id", client_secret="secret"), key_id="k"
    )
    client._auth_manager.ensure_valid_token = MagicMock(return_value="tok")
    return client


def test_default_api_url_follows_config_production():
    """A production-configured ApiConfig (its own default) must not leave
    Judilibre pointed at the sandbox host -- that defeats PISTE_ENV
    switching the same way for both clients."""
    config = ApiConfig(client_id="id", client_secret="secret")
    assert config.api_url == PROD_API_URL

    client = JudilibreClient(config=config, key_id="k")

    assert client.api_url == JUDILIBRE_PROD_URL


def test_default_api_url_follows_config_sandbox():
    config = ApiConfig(client_id="id", client_secret="secret", api_url=SANDBOX_API_URL)
    client = JudilibreClient(config=config, key_id="k")

    assert client.api_url == JUDILIBRE_SANDBOX_URL


def test_explicit_api_url_overrides_config_inference():
    config = ApiConfig(client_id="id", client_secret="secret")
    client = JudilibreClient(config=config, key_id="k", api_url=JUDILIBRE_SANDBOX_URL)

    assert client.api_url == JUDILIBRE_SANDBOX_URL


def test_get_raises_judilibre_api_error_when_retries_exhausted():
    # Patch the module-level retry helper directly instead of driving the
    # real tenacity retry loop, to avoid real sleeps.
    client = _client()
    with patch(
        "pylegifrance.fonds.judilibre._get_with_retry",
        side_effect=_TransientAPIError(503, "still down"),
    ):
        with pytest.raises(JudilibreAPIError) as excinfo:
            client.get("search", params={"query": "x"})

    assert excinfo.value.status_code == 503
    assert excinfo.value.body == "still down"


def test_get_raises_judilibre_api_error_on_non_retryable_4xx():
    client = _client()
    with patch.object(
        client._session,
        "get",
        return_value=MagicMock(status_code=400, text="bad request"),
    ):
        with pytest.raises(JudilibreAPIError) as excinfo:
            client.get("search", params={"query": "x"})

    assert excinfo.value.status_code == 400
    assert excinfo.value.body == "bad request"


def test_close_closes_session_and_auth_manager():
    client = _client()
    client._session.close = MagicMock()
    client._auth_manager.close = MagicMock()

    client.close()

    client._session.close.assert_called_once()
    client._auth_manager.close.assert_called_once()
