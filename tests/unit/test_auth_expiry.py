import time
from unittest.mock import MagicMock

from pylegifrance.auth import AuthenticationManager, TokenInfo
from pylegifrance.config import ApiConfig


def _manager() -> AuthenticationManager:
    return AuthenticationManager(ApiConfig(client_id="id", client_secret="secret"))


def test_ensure_valid_token_refreshes_once_within_expiry_margin():
    manager = _manager()
    manager._fetch_new_token = MagicMock(
        side_effect=[
            TokenInfo(access_token="tok1", issued_at=time.time(), expires_in=3600),
            TokenInfo(access_token="tok2", issued_at=time.time(), expires_in=3600),
        ]
    )

    first = manager.ensure_valid_token()
    assert first == "tok1"
    assert manager._fetch_new_token.call_count == 1

    # Not literally expired yet (3570s < 3600s lifetime), but within the
    # refresh margin: a reasonable client refreshes proactively rather
    # than risk the token expiring mid-request.
    manager._token_info.issued_at -= 3570

    second = manager.ensure_valid_token()
    assert second == "tok2"
    assert manager._fetch_new_token.call_count == 2


def test_is_expired_true_within_margin_of_stated_lifetime():
    token = TokenInfo(access_token="tok", issued_at=time.time() - 3570, expires_in=3600)

    assert token.is_expired is True


def test_is_expired_false_well_within_lifetime():
    token = TokenInfo(access_token="tok", issued_at=time.time(), expires_in=3600)

    assert token.is_expired is False


def test_short_lived_token_is_not_immediately_expired():
    """A token whose expires_in is below the 60s refresh margin must still
    be usable for part of its life, not treated as expired the instant
    it's issued (margin clamping to 0 made elapsed_time >= 0 always true)."""
    token = TokenInfo(access_token="tok", issued_at=time.time(), expires_in=30)

    assert token.is_expired is False


def test_short_lived_token_expires_partway_through_its_life():
    token = TokenInfo(access_token="tok", issued_at=time.time() - 20, expires_in=30)

    assert token.is_expired is True
