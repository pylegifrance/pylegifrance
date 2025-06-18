from dataclasses import dataclass
import os
import logging

from dotenv import load_dotenv


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
    token_url: str = "https://oauth.piste.gouv.fr/api/oauth/token"
    api_url: str = "https://api.piste.gouv.fr/dila/legifrance/lf-engine-app/"
    connect_timeout: float = 3.05  # seconds
    read_timeout: float = 27.0  # seconds

    @classmethod
    def from_env(cls) -> "ApiConfig":
        """
        Create an ApiConfig instance from environment variables.

        Returns:
            ApiConfig: A new ApiConfig instance with values from environment variables.

        Raises:
            ValueError: If required environment variables are not set.
        """
        load_dotenv()

        client_id = os.getenv("LEGIFRANCE_CLIENT_ID")
        client_secret = os.getenv("LEGIFRANCE_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "Required environment variables LEGIFRANCE_CLIENT_ID and/or "
                "LEGIFRANCE_CLIENT_SECRET are not set."
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
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
