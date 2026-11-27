from unittest.mock import MagicMock, patch

import pytest

from pylegifrance.client import LegifranceClient
from pylegifrance.config import ApiConfig


def _client() -> LegifranceClient:
    client = LegifranceClient(ApiConfig(client_id="id", client_secret="secret"))
    client._auth_manager.ensure_valid_token = MagicMock(return_value="tok")
    return client


def test_call_api_retries_on_429_then_succeeds():
    client = _client()
    responses = [
        MagicMock(status_code=429, text="rate limited"),
        MagicMock(status_code=200, text="ok"),
    ]
    with patch.object(client.session, "post", side_effect=responses) as mock_post:
        result = client.call_api("search", {"x": 1})
    assert result.status_code == 200
    assert mock_post.call_count == 2


def test_call_api_does_not_retry_on_400():
    client = _client()
    with patch.object(
        client.session,
        "post",
        return_value=MagicMock(status_code=400, text="bad request"),
    ) as mock_post:
        with pytest.raises(Exception, match="400"):
            client.call_api("search", {"x": 1})
    assert mock_post.call_count == 1
