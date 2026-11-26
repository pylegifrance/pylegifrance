"""Unit tests for LegifranceClient behavior not covered by test_client_retry.py.

Covers: get(), ping(), update_api_keys(), create(), session_context(), close(),
and call_api()'s "no data" guard. Only the requests.Session / AuthenticationManager
boundary is mocked; LegifranceClient itself is exercised directly.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from pylegifrance.client import LegifranceClient, _TransientAPIError
from pylegifrance.config import ApiConfig


def _client() -> LegifranceClient:
    client = LegifranceClient(ApiConfig(client_id="id", client_secret="secret"))
    client._auth_manager.ensure_valid_token = MagicMock(return_value="tok")
    return client


# ---------------------------------------------------------------------------
# call_api: no-data guard
# ---------------------------------------------------------------------------


def test_call_api_raises_value_error_when_data_is_none():
    client = _client()
    with pytest.raises(ValueError, match="No data provided"):
        client.call_api("search", None)


def test_call_api_logs_4xx_at_warning_not_error(caplog):
    """A 4xx is routine for callers that probe for existence (e.g.
    JuriAPI.fetch_by_id's documented "unknown textId" 400) and handle it
    themselves. Logging it at ERROR makes every successful probe look like
    a real failure in the logs; WARNING reflects that call_api itself
    doesn't know whether the caller will treat this as fatal."""
    client = _client()
    mock_response = MagicMock(status_code=400, text="L'expression à valider est fausse")
    with patch("pylegifrance.client._post_with_retry", return_value=mock_response):
        with caplog.at_level("WARNING"):
            with pytest.raises(Exception, match="API client error 400"):
                client.call_api("consult/juri", {"textId": "JURITEXT999999999999"})

    assert any(record.levelname == "WARNING" for record in caplog.records)
    assert not any(record.levelname == "ERROR" for record in caplog.records)


def test_call_api_raises_plain_exception_when_retries_exhausted():
    # Patch the module-level retry helper directly rather than driving the
    # real tenacity retry loop (which would introduce real sleeps); this
    # simulates retries being exhausted and checks that call_api converts
    # the internal _TransientAPIError signal back into the public exception
    # contract (lines 151-156 of client.py).
    client = _client()
    with patch(
        "pylegifrance.client._post_with_retry",
        side_effect=_TransientAPIError(500, "still failing"),
    ):
        with pytest.raises(Exception, match="API client error 500 - still failing"):
            client.call_api("search", {"x": 1})


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


def test_get_sends_bearer_header_and_returns_response():
    client = _client()
    mock_response = MagicMock(status_code=200)
    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        result = client.get("consult/legiPart")

    called_args, called_kwargs = mock_get.call_args
    assert called_args[0] == f"{client.api_url}consult/legiPart"
    assert called_kwargs["headers"]["Authorization"] == "Bearer tok"
    mock_response.raise_for_status.assert_called_once()
    assert result is mock_response


def test_get_raises_for_http_error_status():
    client = _client()
    mock_response = MagicMock(status_code=404)
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
    with patch.object(client.session, "get", return_value=mock_response):
        with pytest.raises(requests.exceptions.HTTPError):
            client.get("consult/missing")


# ---------------------------------------------------------------------------
# ping()
# ---------------------------------------------------------------------------


def test_ping_returns_true_on_200():
    client = _client()
    with patch.object(
        client.session, "get", return_value=MagicMock(status_code=200, text="pong")
    ):
        assert client.ping() is True


def test_ping_returns_false_on_non_200():
    client = _client()
    with patch.object(
        client.session, "get", return_value=MagicMock(status_code=503, text="down")
    ):
        assert client.ping() is False


def test_ping_wraps_request_exception():
    client = _client()
    with patch.object(
        client.session, "get", side_effect=requests.exceptions.ConnectionError("boom")
    ):
        with pytest.raises(Exception, match="API ping failed"):
            client.ping()


def test_ping_uses_custom_route():
    client = _client()
    with patch.object(
        client.session, "get", return_value=MagicMock(status_code=200, text="pong")
    ) as mock_get:
        client.ping(route="custom/ping")

    called_url = mock_get.call_args.args[0]
    assert called_url == f"{client.api_url}custom/ping"


# ---------------------------------------------------------------------------
# update_api_keys()
# ---------------------------------------------------------------------------


def test_update_api_keys_with_explicit_values_updates_auth_manager():
    client = _client()
    client._auth_manager.update_credentials = MagicMock()

    client.update_api_keys(client_id="new_id", client_secret="new_secret")

    client._auth_manager.update_credentials.assert_called_once_with(
        "new_id", "new_secret"
    )


def test_update_api_keys_without_args_loads_from_env(monkeypatch):
    client = _client()
    client._auth_manager.update_credentials = MagicMock()

    monkeypatch.setenv("LEGIFRANCE_CLIENT_ID", "env_id")
    monkeypatch.setenv("LEGIFRANCE_CLIENT_SECRET", "env_secret")
    monkeypatch.setattr("pylegifrance.config.load_dotenv", lambda: None)

    client.update_api_keys()

    client._auth_manager.update_credentials.assert_called_once_with(
        "env_id", "env_secret"
    )


def test_update_api_keys_without_args_and_no_env_raises(monkeypatch):
    client = _client()
    monkeypatch.delenv("LEGIFRANCE_CLIENT_ID", raising=False)
    monkeypatch.delenv("LEGIFRANCE_CLIENT_SECRET", raising=False)
    monkeypatch.setattr("pylegifrance.config.load_dotenv", lambda: None)

    with pytest.raises(ValueError, match="Required environment variables"):
        client.update_api_keys()


# ---------------------------------------------------------------------------
# create() factory
# ---------------------------------------------------------------------------


def test_create_factory_returns_client_instance():
    config = ApiConfig(client_id="id", client_secret="secret")
    client = LegifranceClient.create(config=config)

    assert isinstance(client, LegifranceClient)
    assert client.api_url == config.api_url
    client.close()


# ---------------------------------------------------------------------------
# session_context() / close()
# ---------------------------------------------------------------------------


def test_session_context_closes_session_and_auth_manager_on_exit():
    client = _client()
    client.session.close = MagicMock()
    client._auth_manager.close = MagicMock()

    with client.session_context() as ctx_client:
        assert ctx_client is client
        client.session.close.assert_not_called()

    client.session.close.assert_called_once()
    client._auth_manager.close.assert_called_once()


def test_session_context_closes_even_on_exception():
    client = _client()
    client.session.close = MagicMock()
    client._auth_manager.close = MagicMock()

    with pytest.raises(RuntimeError):
        with client.session_context():
            raise RuntimeError("boom")

    client.session.close.assert_called_once()
    client._auth_manager.close.assert_called_once()


def test_close_closes_session_and_auth_manager():
    client = _client()
    client.session.close = MagicMock()
    client._auth_manager.close = MagicMock()

    client.close()

    client.session.close.assert_called_once()
    client._auth_manager.close.assert_called_once()
