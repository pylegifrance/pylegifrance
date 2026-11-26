import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

SANDBOX_TOKEN_URL = "https://sandbox-oauth.piste.gouv.fr/api/oauth/token"
SANDBOX_API_URL = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app/"
PROD_TOKEN_URL = "https://oauth.piste.gouv.fr/api/oauth/token"
PROD_API_URL = "https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/"

_PISTE_ENV_URLS = {
    "sandbox": (SANDBOX_TOKEN_URL, SANDBOX_API_URL),
    "production": (PROD_TOKEN_URL, PROD_API_URL),
}


@dataclass
class ApiConfig:
    """
    Configuration for the Legifrance API client.

    Attributes:
        client_id: The client ID for the Legifrance API.
        client_secret: The client secret for the Legifrance API.
        token_url: The URL for obtaining access tokens.
        api_url: The base URL for the Legifrance API.
        connect_timeout: Timeout in seconds for establishing connection with server.
        read_timeout: Timeout in seconds for receiving response after connection is established.
    """

    client_id: str
    client_secret: str
    token_url: str = PROD_TOKEN_URL
    api_url: str = PROD_API_URL
    connect_timeout: float = 3.05  # seconds
    read_timeout: float = 27.0  # seconds

    @classmethod
    def from_env(cls) -> "ApiConfig":
        """
        Create an ApiConfig instance from environment variables.

        Reads ``PISTE_ENV`` (``"sandbox"`` or ``"production"``, case-insensitive,
        defaults to ``"production"`` to match this class's own field defaults
        and the behavior of callers who upgrade without setting it) to select
        the matching token/API base URLs.

        Returns:
            ApiConfig: A new ApiConfig instance with values from environment variables.

        Raises:
            ValueError: If required environment variables are not set, or if
                PISTE_ENV is set to anything other than "sandbox"/"production".
        """
        load_dotenv()

        client_id = os.getenv("LEGIFRANCE_CLIENT_ID")
        client_secret = os.getenv("LEGIFRANCE_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "Required environment variables LEGIFRANCE_CLIENT_ID and/or "
                "LEGIFRANCE_CLIENT_SECRET are not set."
            )

        piste_env = os.getenv("PISTE_ENV", "production").strip().lower()
        try:
            token_url, api_url = _PISTE_ENV_URLS[piste_env]
        except KeyError:
            raise ValueError(
                f"Invalid PISTE_ENV: {piste_env!r}. Expected 'sandbox' or 'production'."
            ) from None

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            api_url=api_url,
        )


# Formatting keys for API responses
ARTICLE_KEYS = [
    "pathTitle",
    "content",
    "num",
    "fullSectionsTitre",
    "texte",
    "etat",
    "VersionArticle",
    "cid",
]

ROOT_KEYS = ["cid", "title"]

SECTION_KEYS = ["title", "cid"]

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
