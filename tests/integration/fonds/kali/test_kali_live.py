"""Live integration test for the KALI façade.

Hits the real Legifrance API and therefore requires valid credentials
via the ``api_client`` fixture (``tests/conftest.py`` — reads
``LEGIFRANCE_CLIENT_ID`` / ``LEGIFRANCE_CLIENT_SECRET`` from the
environment).

Uses IDCC ``1261`` (« Acteurs du lien social et familial ») because it
is the example cited in the DILA-generated schema
(``KaliContConsultIdccRequest.examples = ["1261"]``,
``ConsultKaliContResponse.id examples = ["KALICONT000005635384"]``).
"""

import pytest

from pylegifrance.fonds.kali import ConventionCollective, KaliAPI

LEGIFRANCE_KALI_BASE = "https://www.legifrance.gouv.fr/conv_coll/id/"


@pytest.fixture(scope="module")
def kali_api(api_client) -> KaliAPI:
    return KaliAPI(api_client)


def test_fetch_by_idcc_1261_returns_real_convention(kali_api: KaliAPI) -> None:
    """Fetch IDCC 1261 live and surface a browseable legifrance.gouv.fr URL.

    Run with ``pytest -s`` to see the URL printed to stdout. The URL is
    also embedded in the assertion message so it appears on failure
    too.
    """
    convention = kali_api.fetch_by_idcc("1261")

    assert convention is not None, "IDCC 1261 doit résoudre sur l'API live"
    assert isinstance(convention, ConventionCollective)
    assert convention.id is not None and convention.id.startswith("KALICONT")
    assert convention.idcc == "1261"

    url = f"{LEGIFRANCE_KALI_BASE}{convention.id}"
    print(f"\n  IDCC 1261 → {convention.titre!r}\n  URL: {url}\n")

    assert url.startswith("https://www.legifrance.gouv.fr/conv_coll/id/KALICONT"), (
        f"URL attendue au format /conv_coll/id/KALICONT..., obtenue: {url}"
    )
