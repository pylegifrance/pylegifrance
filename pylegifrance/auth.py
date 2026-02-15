"""Authentication manager for the Legifrance API.

This module provides a class for handling authentication with the Legifrance API,
including token acquisition, storage, and refresh logic.
"""

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass

import requests
from tenacity import RetryError, retry, stop_after_attempt, wait_fixed

from pylegifrance.config import ApiConfig
from pylegifrance.utils import configure_session_timeouts

logger = logging.getLogger(__name__)


@dataclass
class TokenInfo:
    """
    Stores information about an authentication token.

    Attributes:
        access_token: The actual token string used for authentication.
        issued_at: Timestamp when the token was obtained.
        expires_in: Token lifetime in seconds.
    """

    access_token: str
    issued_at: float
    expires_in: int

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        if not self.access_token:
            return True
        elapsed_time = time.time() - self.issued_at
        return elapsed_time >= self.expires_in

    @property
    def is_valid(self) -> bool:
        """Check if the token is valid and not expired."""
        return bool(self.access_token) and not self.is_expired


class AuthenticationManager:
    """
    Manages authentication with the Legifrance API.

    This class handles token acquisition, storage, and refresh logic.
    It is designed to be used by the LegifranceClient but can also be used independently.

    The manager encapsulates all authentication concerns, including:
    - Storing and managing API credentials
    - Obtaining access tokens
    - Refreshing expired tokens
    - Providing valid tokens for API requests
    """

    def __init__(self, config: ApiConfig):
        """Initialize a new AuthenticationManager instance.

        Args:
            config: Configuration for the API authentication.
        """
        self._client_id = config.client_id
        self._client_secret = config.client_secret
        self._token_url = config.token_url
        self._token_info = TokenInfo(access_token="", issued_at=0, expires_in=0)
        self._session = requests.Session()

        configure_session_timeouts(self._session, config)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5), reraise=True)
    def _fetch_new_token(self) -> TokenInfo:
        """Fetch a new access token from the Legifrance API.

        Returns:
            Information about the newly acquired token.

        Raises:
            Exception: If the token acquisition fails.
        """
        data = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": "openid",
        }

        response = self._session.post(self._token_url, data=data)
        if 200 <= response.status_code < 300:
            response_data = response.json()
            token_info = TokenInfo(
                access_token=response_data.get("access_token", ""),
                issued_at=time.time(),
                expires_in=response_data.get("expires_in", 0),
            )
            logger.info("Legifrance API authentication successful.")
            return token_info
        else:
            logger.warning(
                f"Failed to get token: {response.status_code} - {response.text}"
            )
            raise Exception(
                f"Error obtaining token: {response.status_code} - {response.text}"
            )

    def update_credentials(self, client_id: str, client_secret: str) -> None:
        """Update the authentication credentials.

        Args:
            client_id: The new client ID.
            client_secret: The new client secret.
        """
        if self._client_id != client_id or self._client_secret != client_secret:
            self._client_id = client_id
            self._client_secret = client_secret
            # Reset token state
            self._token_info = TokenInfo(access_token="", issued_at=0, expires_in=0)

    def ensure_valid_token(self) -> str:
        """Ensure that a valid token is available, refreshing it if necessary.

        Returns:
            The valid access token.

        Raises:
            Exception: If the token acquisition or refresh fails.
        """
        if not self._token_info.is_valid:
            try:
                self._token_info = self._fetch_new_token()
            except RetryError as exc:
                logger.error(f"Could not obtain access token after retries: {exc}")
                raise

        return self._token_info.access_token

    def close(self) -> None:
        """
        Close the session used for token acquisition.

        This should be called when the manager is no longer needed to free up resources.
        """
        self._session.close()

    @contextmanager
    def session_context(self):
        """Context manager for using the authentication manager in a with statement.

        This ensures that the session is properly closed after use.

        Yields:
            The authentication manager instance.
        """
        try:
            yield self
        finally:
            self.close()
