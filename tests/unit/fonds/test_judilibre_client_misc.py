"""Unit tests for JudilibreClient error handling and close(), not covered by
test_judilibre_client.py / test_judilibre_client_retry.py. Only the
requests.Session / AuthenticationManager boundary is mocked.
"""

from unittest.mock import MagicMock, patch

import pytest

from pylegifrance.client import _TransientAPIError
from pylegifrance.config import ApiConfig
from pylegifrance.fonds.judilibre import JudilibreAPIError, JudilibreClient


def _client() -> JudilibreClient:
    client = JudilibreClient(
        config=ApiConfig(client_id="id", client_secret="secret"), key_id="k"
    )
    client._auth_manager.ensure_valid_token = MagicMock(return_value="tok")
    return client


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
