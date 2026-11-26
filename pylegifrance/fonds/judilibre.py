"""Client for the Judilibre API (Cour de cassation jurisprudence).

Judilibre is hosted on a different PISTE host than Légifrance's own API and
authenticates with an additional ``KeyId`` header on top of the normal PISTE
bearer token (see docs/superpowers/specs and the Judilibre OpenAPI spec).
"""

from typing import Any

import requests

from pylegifrance.auth import AuthenticationManager
from pylegifrance.config import ApiConfig
from pylegifrance.utils import configure_session_timeouts

JUDILIBRE_SANDBOX_URL = "https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0"
JUDILIBRE_PROD_URL = "https://api.piste.gouv.fr/cassation/judilibre/v1.0"


class JudilibreClient:
    """Client for interacting with the Judilibre API.

    Attributes:
        api_url: The base URL for the Judilibre API.
    """

    def __init__(
        self,
        config: ApiConfig,
        key_id: str,
        api_url: str | None = None,
    ):
        """Initialize a new JudilibreClient instance.

        Args:
            config: PISTE OAuth2 credentials/token URL (same as Légifrance's).
            key_id: The Judilibre-specific ``KeyId`` header value for the
                subscribed PISTE application.
            api_url: The base URL for the Judilibre API. Defaults to the
                sandbox host.
        """
        self.api_url = api_url or JUDILIBRE_SANDBOX_URL
        self._key_id = key_id
        self._auth_manager = AuthenticationManager(config)
        self._session = requests.Session()

        configure_session_timeouts(self._session, config)

    def get(self, route: str, params: dict[str, Any] | None = None) -> requests.Response:
        """Call the Judilibre API with token management and error logging.

        Args:
            route: The API route to use (e.g. ``"search"``, ``"decision"``).
            params: Query parameters to send.

        Returns:
            The API response.

        Raises:
            Exception: If the API call fails or authentication fails.
        """
        token = self._auth_manager.ensure_valid_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "KeyId": self._key_id,
            "accept": "application/json",
        }

        url = f"{self.api_url}/{route}"
        response = self._session.get(url, headers=headers, params=params)

        if 400 <= response.status_code < 600:
            raise Exception(
                f"API client error {response.status_code} - {response.text}"
            )

        return response

    def close(self) -> None:
        """Close the client's session and authentication manager."""
        self._session.close()
        self._auth_manager.close()
