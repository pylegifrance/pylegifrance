import json
import logging
from contextlib import contextmanager
from typing import Any, Self

import requests

from pylegifrance.auth import AuthenticationManager
from pylegifrance.config import ApiConfig
from pylegifrance.utils import configure_session_timeouts

logger = logging.getLogger(__name__)


class LegifranceClient:
    """
    Client for interacting with the Legifrance API.

    This class provides methods for making requests to the API.
    Authentication is handled by a separate AuthenticationManager.

    The client delegates all authentication concerns to the AuthenticationManager,
    focusing solely on making API requests and processing responses.

    Attributes:
        api_url: The base URL for the Legifrance API.
        session: The requests session used for making API calls.
    """

    def __init__(self, config: ApiConfig | None = None):
        """Initialize a new LegifranceClient instance.

        Args:
            config: Configuration for the API client. If None, will attempt to load
                from environment variables.

        Raises:
            ValueError: If config is not provided and environment variables are not set.
        """
        if config is None:
            try:
                config = ApiConfig.from_env()
            except ValueError as e:
                logger.error(f"Failed to initialize API client: {e}")
                raise

        self.api_url = config.api_url
        self._auth_manager = AuthenticationManager(config)
        self.session = requests.Session()

        configure_session_timeouts(self.session, config)

    def update_api_keys(
        self, client_id: str | None = None, client_secret: str | None = None
    ) -> None:
        """Update the API keys for the client.

        If keys are provided, they replace the current values.
        If keys are not provided, the method attempts to retrieve them
        from environment variables.

        Args:
            client_id: Legifrance API key. If None, attempts to retrieve from
                environment variable.
            client_secret: Legifrance API secret. If None, attempts to retrieve from
                environment variable.

        Raises:
            ValueError: If keys are not provided and cannot be retrieved
                from environment variables.
        """
        if client_id is not None and client_secret is not None:
            # Use provided keys
            self._auth_manager.update_credentials(client_id, client_secret)
        else:
            # Try to load from environment
            try:
                new_config = ApiConfig.from_env()
                self._auth_manager.update_credentials(
                    new_config.client_id, new_config.client_secret
                )
            except ValueError as e:
                logger.error(f"Failed to set API keys: {e}")
                raise

    def call_api(self, route: str, data: Any) -> requests.Response:
        """Call the Legifrance API with token management and error logging.

        Args:
            route: The API route to use.
            data: The data to send as JSON.

        Returns:
            The API response.

        Raises:
            ValueError: If no data is provided.
            Exception: If the API call fails or authentication fails.
        """
        if data is None:
            logger.warning("No data provided to call_api; request not sent.")
            raise ValueError("No data provided for API call.")

        token = self._auth_manager.ensure_valid_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        url = f"{self.api_url}{route}"
        logger.debug(
            f"Payload for request {url}: {json.dumps(data, indent=2, ensure_ascii=False)}"
        )
        response = self.session.post(url, headers=headers, json=data)

        if 400 <= response.status_code < 600:
            logger.error(
                f"Client error {response.status_code} - {response.text} when calling the API."
            )
            raise Exception(
                f"API client error {response.status_code} - {response.text}"
            )

        logger.info(f"API call to '{route}' successful.")
        return response

    def get(self, route: str) -> requests.Response:
        """Perform a GET request on the given API route.

        Args:
            route: The route to target.

        Returns:
            The API response.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request returns an unsuccessful
                status code.
            Exception: If authentication fails.
        """
        token = self._auth_manager.ensure_valid_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self.api_url}{route}"

        logger.info(f"GET request to URL: {url}")
        response = self.session.get(url, headers=headers)
        response.raise_for_status()

        logger.info(f"GET request successful for URL: {url}")
        return response

    def ping(self, route: str = "consult/ping") -> bool:
        """Check connectivity with the Legifrance API by sending a ping request.

        Args:
            route: Route to use for the ping (default: "consult/ping").

        Returns:
            True if the connection is successful, otherwise False.

        Raises:
            Exception: In case of API connection error or authentication failure.
        """
        try:
            token = self._auth_manager.ensure_valid_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "text/plain",
                "Content-Type": "application/json",
            }

            url = f"{self.api_url}{route}"
            response = self.session.get(url, headers=headers)

            if response.status_code == 200:
                logger.debug(
                    "Ping successful: connection to Legifrance API established."
                )
                return True
            else:
                logger.warning(
                    f"Ping failed: return code {response.status_code} - {response.text}"
                )
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during Legifrance API ping: {str(e)}")
            raise Exception(f"API ping failed: {e}") from e

    @classmethod
    def create(cls, config: ApiConfig | None = None) -> Self:
        """Factory method to create a new LegifranceClient instance.

        Args:
            config: Configuration for the API client. If None, will attempt to load
                from environment variables.

        Returns:
            A new instance of LegifranceClient.
        """
        return cls(config=config)

    @contextmanager
    def session_context(self):
        """Context manager for using the client in a with statement.

        This ensures that the session is properly closed after use.

        Yields:
            The client instance.
        """
        try:
            yield self
        finally:
            self.close()

    def close(self) -> None:
        """
        Close the client's session and authentication manager.

        This should be called when the client is no longer needed to free up resources.
        """
        self.session.close()
        self._auth_manager.close()
