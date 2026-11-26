"""Client for the Judilibre API (Cour de cassation jurisprudence).

Judilibre is hosted on a different PISTE host than Légifrance's own API and
authenticates with an additional ``KeyId`` header on top of the normal PISTE
bearer token (see docs/superpowers/specs and the Judilibre OpenAPI spec).
"""

from typing import Any

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pylegifrance.auth import AuthenticationManager
from pylegifrance.client import _TransientAPIError, _is_retryable_status
from pylegifrance.config import ApiConfig
from pylegifrance.models.judilibre.models import DecisionFull, DecisionShort
from pylegifrance.utils import configure_session_timeouts

JUDILIBRE_SANDBOX_URL = "https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0"
JUDILIBRE_PROD_URL = "https://api.piste.gouv.fr/cassation/judilibre/v1.0"

HTTP_OK = 200
HTTP_NOT_FOUND = 404

COUR_DE_CASSATION_URL_TEMPLATE = "https://www.courdecassation.fr/decision/{id}"


class JudilibreAPIError(Exception):
    """A Judilibre API error, after retries for transient (429/5xx) statuses
    are exhausted. Carries the HTTP status code so callers (notably
    :meth:`JudilibreAPI.fetch`) can distinguish "not found" (404) from a
    real failure, rather than every non-2xx response collapsing into the
    same generic exception.
    """

    def __init__(self, status_code: int, body: str):
        self.status_code = status_code
        self.body = body
        super().__init__(f"API client error {status_code} - {body}")


@retry(
    retry=retry_if_exception_type(_TransientAPIError),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _get_with_retry(
    session: requests.Session,
    url: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
) -> requests.Response:
    response = session.get(url, headers=headers, params=params)
    # 404 is not retried: it's Judilibre's legitimate "not found" answer on
    # /decision, not a transient failure. It still raises JudilibreAPIError
    # below like every other non-2xx status — JudilibreAPI.fetch is what
    # interprets a 404 specifically as "no such decision"; JudilibreClient
    # itself never silently swallows an error into a successful response.
    if _is_retryable_status(response.status_code):
        raise _TransientAPIError(response.status_code, response.text)
    return response


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
        try:
            response = _get_with_retry(self._session, url, headers, params)
        except _TransientAPIError as exc:
            raise JudilibreAPIError(exc.status_code, exc.body) from exc

        if 400 <= response.status_code < 600:
            raise JudilibreAPIError(response.status_code, response.text)

        return response

    def close(self) -> None:
        """Close the client's session and authentication manager."""
        self._session.close()
        self._auth_manager.close()


def _clean_params(params: dict[str, Any]) -> dict[str, Any]:
    """Drop None-valued entries so they are not sent as query parameters."""
    return {k: v for k, v in params.items() if v is not None}


class JudilibreDecision:
    """High-level domain object wrapping a Judilibre decision."""

    def __init__(self, decision: DecisionShort | DecisionFull):
        self._decision = decision

    @property
    def id(self) -> str:
        return self._decision.id

    @property
    def jurisdiction(self) -> str | None:
        return self._decision.jurisdiction

    @property
    def chamber(self) -> str | None:
        return self._decision.chamber

    @property
    def ecli(self) -> str | None:
        return self._decision.ecli

    @property
    def decision_date(self) -> str | None:
        return self._decision.decision_date

    @property
    def summary(self) -> str | None:
        return self._decision.summary

    @property
    def solution(self) -> str | None:
        return self._decision.solution

    @property
    def text(self) -> str | None:
        return getattr(self._decision, "text", None)

    @property
    def update_date(self) -> str | None:
        return getattr(self._decision, "update_date", None)

    @property
    def url(self) -> str | None:
        """The source URL, for Licence Ouverte attribution.

        Prefers the first file link (present on decisions with attached
        documents). Most decisions have no files, so this falls back to
        the canonical courdecassation.fr decision URL built from the
        decision's own id — best-effort, not verified against a live
        Judilibre response at the time of writing.
        """
        files = self._decision.files
        if files:
            url = files[0].get("url")
            if url:
                return url
        if self.id:
            return COUR_DE_CASSATION_URL_TEMPLATE.format(id=self.id)
        return None

    def to_markdown(self) -> str:
        """Markdown representation of the decision, optimized for LLMs."""
        parts: list[str] = []

        heading_parts = [p for p in [self.jurisdiction, self.chamber] if p]
        if self.decision_date:
            heading_parts.append(self.decision_date)
        parts.append(f"## {', '.join(heading_parts) or 'Décision'}")
        parts.append("")

        if self.solution:
            parts.append(f"**Solution**: {self.solution}")
        if self.ecli:
            parts.append(f"**ECLI**: {self.ecli}")
        if self.id:
            parts.append(f"**Référence**: {self.id}")
        if self.url:
            parts.append(f"**URL**: {self.url}")
        parts.append("")

        if self.summary:
            parts.append(f"**Sommaire**: {self.summary}")
            parts.append("")

        if self.text:
            parts.append(self.text)

        return "\n".join(parts)


class JudilibreAPI:
    """High-level API for searching and fetching Judilibre decisions."""

    def __init__(self, client: JudilibreClient):
        self._client = client

    def search(self, query: str, **filters: Any) -> list[JudilibreDecision]:
        """Search Judilibre decisions matching ``query`` and the given filters.

        Args:
            query: Full-text search query.
            **filters: Any of Judilibre's documented search filters
                (``jurisdiction``, ``chamber``, ``date_start``, ``date_end``,
                ``page_size``, ...), passed through as query parameters.

        Returns:
            A list of matching decisions (summary fields only).
        """
        params = _clean_params({"query": query, **filters})
        # client.get() raises JudilibreAPIError on 4xx/5xx; this check is
        # only a defensive fallback for a non-OK 2xx (e.g. 204), not for
        # errors, which never reach this line.
        response = self._client.get("search", params=params)
        if response.status_code != HTTP_OK:
            return []

        data = response.json()
        results = data.get("results") or []
        return [JudilibreDecision(DecisionShort(**r)) for r in results]

    def fetch(self, decision_id: str) -> JudilibreDecision | None:
        """Fetch the full text of a decision by its Judilibre id.

        Args:
            decision_id: The Judilibre decision identifier.

        Returns:
            The decision, or ``None`` if no decision matches the id.
        """
        try:
            response = self._client.get("decision", params={"id": decision_id})
        except JudilibreAPIError as exc:
            if exc.status_code == HTTP_NOT_FOUND:
                return None
            raise

        if response.status_code != HTTP_OK:
            return None

        data = response.json()
        return JudilibreDecision(DecisionFull(**data))
