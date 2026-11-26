from unittest.mock import MagicMock, patch

from pylegifrance.config import ApiConfig
from pylegifrance.fonds.judilibre import JUDILIBRE_SANDBOX_URL, JudilibreClient


def test_get_sends_bearer_and_keyid_headers():
    config = ApiConfig(client_id="id", client_secret="secret")
    client = JudilibreClient(
        config=config, key_id="my-key-id", api_url=JUDILIBRE_SANDBOX_URL
    )
    client._auth_manager.ensure_valid_token = MagicMock(return_value="tok123")

    with patch.object(client._session, "get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        client.get("search", params={"query": "brevet"})

    called_url = mock_get.call_args.args[0]
    called_headers = mock_get.call_args.kwargs["headers"]
    assert called_url == f"{JUDILIBRE_SANDBOX_URL}/search"
    assert called_headers["Authorization"] == "Bearer tok123"
    assert called_headers["KeyId"] == "my-key-id"
