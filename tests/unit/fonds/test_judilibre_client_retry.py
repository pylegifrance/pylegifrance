from unittest.mock import MagicMock, patch

from pylegifrance.config import ApiConfig
from pylegifrance.fonds.judilibre import JudilibreClient


def test_get_retries_on_503_then_succeeds():
    client = JudilibreClient(
        config=ApiConfig(client_id="id", client_secret="secret"), key_id="k"
    )
    client._auth_manager.ensure_valid_token = MagicMock(return_value="tok")
    responses = [
        MagicMock(status_code=503, text="unavailable"),
        MagicMock(status_code=200, text="ok"),
    ]
    with patch.object(client._session, "get", side_effect=responses) as mock_get:
        result = client.get("search", params={"query": "x"})
    assert result.status_code == 200
    assert mock_get.call_count == 2
