"""Unit tests for the :class:`pylegifrance.fonds.juri.JuriDecision` wrapper.

These tests focus on behaviour that does not require the Legifrance API,
notably the :pyattr:`JuriDecision.url` auto-generation that mirrors the
canonical URL logic already present on :class:`Article`.
"""

from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.juri import JuriDecision
from pylegifrance.models.juri.models import Decision


def _make_decision(decision_id: str | None) -> JuriDecision:
    """Build a :class:`JuriDecision` around a minimally populated model."""
    decision = Decision(id=decision_id) if decision_id is not None else Decision()
    client = MagicMock()
    return JuriDecision(decision=decision, client=client)


class TestJuriDecisionUrl:
    """Auto-generated Legifrance URL on :class:`JuriDecision`."""

    def test_url_from_juritext_id(self):
        """A JURITEXT id yields the canonical Legifrance consultation URL."""
        decision = _make_decision("JURITEXT000027546700")

        assert (
            decision.url
            == "https://www.legifrance.gouv.fr/juri/id/JURITEXT000027546700"
        )

    def test_url_from_cetatext_id(self):
        """A CETATEXT id (Conseil d'Etat) also resolves under /juri/id/."""
        decision = _make_decision("CETATEXT000007422435")

        assert (
            decision.url
            == "https://www.legifrance.gouv.fr/juri/id/CETATEXT000007422435"
        )

    def test_url_is_none_when_id_is_none(self):
        """A decision with no id must not emit a malformed URL."""
        decision = _make_decision(None)

        assert decision.url is None

    def test_url_is_none_when_id_is_empty(self):
        """An empty id must yield ``None`` rather than a dangling URL."""
        decision = _make_decision("")

        assert decision.url is None

    def test_url_is_none_for_unknown_prefix(self):
        """Identifiers with unrecognised prefixes must not be URL-ified.

        Only JURITEXT and CETATEXT are known to resolve under
        ``/juri/id/`` on legifrance.gouv.fr. Anything else would produce
        a broken link and is therefore refused.
        """
        decision = _make_decision("LEGIARTI000006419292")

        assert decision.url is None

    @pytest.mark.parametrize(
        "decision_id",
        [
            "JURITEXT000041234567",
            "JURITEXT000000254716",
            "CETATEXT000007422435",
        ],
    )
    def test_url_is_prefixed_with_legifrance_host(self, decision_id):
        """Every generated URL targets the official Legifrance host."""
        decision = _make_decision(decision_id)

        assert decision.url is not None
        assert decision.url.startswith("https://www.legifrance.gouv.fr/juri/id/")
        assert decision.url.endswith(decision_id)
