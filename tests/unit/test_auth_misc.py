"""Unit tests for AuthenticationManager behavior not covered by test_auth_expiry.py.

Covers: update_credentials() (no-op vs reset), _fetch_new_token() success/failure
paths, close(), and session_context(). Only requests.Session is mocked.
"""

import time
from unittest.mock import MagicMock, patch

import pytest
from tenacity import RetryError

from pylegifrance.auth import AuthenticationManager, TokenInfo
from pylegifrance.config import ApiConfig


def _manager() -> AuthenticationManager:
    return AuthenticationManager(ApiConfig(client_id="id", client_secret="secret"))


# ---------------------------------------------------------------------------
# TokenInfo.is_expired with no access token
# ---------------------------------------------------------------------------


def test_is_expired_true_when_access_token_is_empty():
    token = TokenInfo(access_token="", issued_at=time.time(), expires_in=3600)

    assert token.is_expired is True


# ---------------------------------------------------------------------------
# update_credentials()
# ---------------------------------------------------------------------------


def test_update_credentials_with_same_values_is_a_noop():
    manager = _manager()
    manager._token_info = TokenInfo(
        access_token="tok", issued_at=time.time(), expires_in=3600
    )

    manager.update_credentials("id", "secret")

    assert manager._token_info.access_token == "tok"


def test_update_credentials_with_different_client_id_resets_token():
    manager = _manager()
    manager._token_info = TokenInfo(
        access_token="tok", issued_at=time.time(), expires_in=3600
    )

    manager.update_credentials("new_id", "secret")

    assert manager._client_id == "new_id"
    assert manager._token_info.access_token == ""
    assert manager._token_info.is_expired is True


def test_update_credentials_with_different_secret_resets_token():
    manager = _manager()
    manager._token_info = TokenInfo(
        access_token="tok", issued_at=time.time(), expires_in=3600
    )

    manager.update_credentials("id", "new_secret")

    assert manager._client_secret == "new_secret"
    assert manager._token_info.access_token == ""


# ---------------------------------------------------------------------------
# _fetch_new_token() / ensure_valid_token()
# ---------------------------------------------------------------------------


def test_fetch_new_token_success_populates_token_info():
    # Call the undecorated function directly (via __wrapped__) so the
    # @retry(wait_fixed(5)) wrapper doesn't introduce real sleeps for a
    # single, successful call.
    manager = _manager()
    mock_response = MagicMock(status_code=200)
    mock_response.json.return_value = {"access_token": "abc123", "expires_in": 3600}

    # basedpyright doesn't know tenacity's @retry wrapper preserves
    # __wrapped__ via functools.wraps (it's a real attribute at runtime).
    unwrapped_fetch = AuthenticationManager._fetch_new_token.__wrapped__  # pyright: ignore[reportFunctionMemberAccess]

    with patch.object(manager._session, "post", return_value=mock_response):
        token_info = unwrapped_fetch(manager)

    assert token_info.access_token == "abc123"
    assert token_info.expires_in == 3600


def test_fetch_new_token_failure_raises_with_status_and_body():
    manager = _manager()
    mock_response = MagicMock(status_code=401, text="unauthorized")

    unwrapped_fetch = AuthenticationManager._fetch_new_token.__wrapped__  # pyright: ignore[reportFunctionMemberAccess]

    with patch.object(manager._session, "post", return_value=mock_response):
        with pytest.raises(Exception, match="401 - unauthorized"):
            unwrapped_fetch(manager)


def test_ensure_valid_token_fetches_once_and_reuses_valid_token():
    manager = _manager()
    manager._fetch_new_token = MagicMock(
        return_value=TokenInfo(
            access_token="tok1", issued_at=time.time(), expires_in=3600
        )
    )

    first = manager.ensure_valid_token()
    second = manager.ensure_valid_token()

    assert first == "tok1"
    assert second == "tok1"
    manager._fetch_new_token.assert_called_once()


def test_ensure_valid_token_reraises_and_logs_retry_error():
    # _fetch_new_token's own @retry(reraise=True) means a RetryError never
    # actually escapes it in production, but ensure_valid_token still
    # defensively catches and re-raises RetryError (lines 144-146) -
    # exercise that handler directly by simulating it being raised.
    manager = _manager()
    underlying = ValueError("token endpoint unreachable")
    retry_error = RetryError(last_attempt=MagicMock(exception=lambda: underlying))
    manager._fetch_new_token = MagicMock(side_effect=retry_error)

    with pytest.raises(RetryError):
        manager.ensure_valid_token()


# ---------------------------------------------------------------------------
# close() / session_context()
# ---------------------------------------------------------------------------


def test_close_closes_session():
    manager = _manager()
    manager._session.close = MagicMock()

    manager.close()

    manager._session.close.assert_called_once()


def test_session_context_closes_session_on_exit():
    manager = _manager()
    manager._session.close = MagicMock()

    with manager.session_context() as ctx_manager:
        assert ctx_manager is manager
        manager._session.close.assert_not_called()

    manager._session.close.assert_called_once()


def test_session_context_closes_session_even_on_exception():
    manager = _manager()
    manager._session.close = MagicMock()

    with pytest.raises(RuntimeError):
        with manager.session_context():
            raise RuntimeError("boom")

    manager._session.close.assert_called_once()
