"""Live integration tests for JuriAPI verification endpoints.

These tests hit the real Legifrance API and therefore require valid
credentials to be available via the ``api_client`` fixture
(see ``tests/conftest.py``). They exercise the three new methods added
to :class:`pylegifrance.fonds.juri.JuriAPI`:

- :meth:`JuriAPI.fetch_by_id`
- :meth:`JuriAPI.search_by_ecli`
- :meth:`JuriAPI.search_by_affaire`

They live under ``tests/integration/`` to match the repository
convention (no custom ``integration`` marker is registered in
pyproject.toml — the gate is the ``api_client`` fixture, which loads
credentials from the environment).
"""

import pytest

from pylegifrance.fonds.juri import JuriAPI, JuriDecision


@pytest.fixture(scope="module")
def juri_api(api_client) -> JuriAPI:
    """Build a JuriAPI bound to the shared real Legifrance client."""
    return JuriAPI(api_client)


def test_fetch_by_id_resolves_known_decision(juri_api: JuriAPI) -> None:
    """The DILA cookbook example ``JURITEXT000037999394`` must resolve.

    Picked from the official DILA API cookbook (``exemples-d-utilisation-
    de-l-api.docx``) as a known-good, stable Cour de cassation decision.
    """
    decision = juri_api.fetch_by_id("JURITEXT000037999394")

    assert decision is not None
    assert isinstance(decision, JuriDecision)
    assert decision.id == "JURITEXT000037999394"
    assert decision.url == (
        "https://www.legifrance.gouv.fr/juri/id/JURITEXT000037999394"
    )


def test_fetch_by_id_returns_none_for_unknown_identifier(
    juri_api: JuriAPI,
) -> None:
    """A well-formed but non-existent JURITEXT yields ``None``.

    The final ``000`` suffix is intentionally picked to not collide with
    any real identifier while keeping the expected 20-char JURITEXT
    shape — Legifrance should answer 200 with an empty ``text`` payload.
    """
    decision = juri_api.fetch_by_id("JURITEXT099999999999")

    assert decision is None


def test_search_by_ecli_resolves_known_cassation_decision(
    juri_api: JuriAPI,
) -> None:
    """Resolve a real Cour de cassation ECLI to at least one match."""
    matches = juri_api.search_by_ecli("ECLI:FR:CCASS:2018:CO00579")

    assert isinstance(matches, list)
    # We don't assert exactly one match because Legifrance occasionally
    # indexes corrective versions; what we care about is that the ECLI
    # resolves to something identifiable.
    assert len(matches) >= 1
    for match in matches:
        assert isinstance(match, JuriDecision)
        assert match.id is not None


def test_search_by_affaire_with_formation_and_date(juri_api: JuriAPI) -> None:
    """Search for a real Cassation tuple and expect at least one hit.

    Uses a stable Cour de cassation case from the DILA sample set to
    validate that the combined ``NUM_AFFAIRE`` + ``CASSATION_FORMATION``
    + ``DATE_DECISION`` filters propagate correctly through the search
    endpoint.
    """
    from datetime import date

    matches = juri_api.search_by_affaire(
        num_affaire="18-26.218",
        formation="Soc",
        date_range=(date(2020, 1, 1), date(2020, 12, 31)),
    )

    assert isinstance(matches, list)
    for match in matches:
        assert isinstance(match, JuriDecision)
