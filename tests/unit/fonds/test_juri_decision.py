"""Unit tests for the :class:`pylegifrance.fonds.juri.JuriDecision` wrapper.

These tests focus on behaviour that does not require the Legifrance API,
notably the :pyattr:`JuriDecision.url` auto-generation that mirrors the
canonical URL logic already present on :class:`Article`.
"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.juri import JuriDecision
from pylegifrance.models.generated.model import TexteSommaire
from pylegifrance.models.juri.models import Decision


def _make_decision(decision_id: str | None) -> JuriDecision:
    """Build a :class:`JuriDecision` around a minimally populated model."""
    decision = Decision(id=decision_id) if decision_id is not None else Decision()
    client = MagicMock()
    return JuriDecision(decision=decision, client=client)


def _make_decision_with(**fields: Any) -> JuriDecision:
    """Build a :class:`JuriDecision` with arbitrary :class:`Decision` fields."""
    decision = Decision(**fields)
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


class TestJuriDecisionSommaire:
    """Sommaire / headnote / titrages exposure on :class:`JuriDecision`."""

    def test_sommaire_returns_empty_list_when_unset(self):
        """A decision without a sommaire returns ``[]``, not ``None``."""
        decision = _make_decision(None)

        assert decision.sommaire == []

    def test_sommaire_returns_list_when_populated(self):
        """The sommaire list is exposed verbatim, preserving its entries."""
        entries = [
            TexteSommaire(
                id="1",
                resumePrincipal="Coemployeurs - Notion - Critères",
                abstrats="Une société d'un groupe ne peut être coemployeur...",
            ),
        ]
        decision = _make_decision_with(sommaire=entries)

        assert decision.sommaire == entries
        assert decision.sommaire[0].abstrats.startswith("Une société")

    def test_headnote_returns_first_resume_principal(self):
        """``headnote`` is the convenience accessor on ``sommaire[0].resume_principal``."""
        entries = [
            TexteSommaire(id="1", resumePrincipal="Forfait jours - Nullité"),
            TexteSommaire(id="2", resumePrincipal="Autre point de droit"),
        ]
        decision = _make_decision_with(sommaire=entries)

        assert decision.headnote == "Forfait jours - Nullité"

    def test_headnote_skips_empty_resume_principal(self):
        """``headnote`` returns the first NON-empty ``resume_principal``."""
        entries = [
            TexteSommaire(id="1", resumePrincipal=None),
            TexteSommaire(id="2", resumePrincipal=""),
            TexteSommaire(id="3", resumePrincipal="Travail de nuit - Repos"),
        ]
        decision = _make_decision_with(sommaire=entries)

        assert decision.headnote == "Travail de nuit - Repos"

    def test_headnote_is_none_when_sommaire_missing(self):
        """A decision without any sommaire has no headnote."""
        decision = _make_decision(None)

        assert decision.headnote is None

    def test_headnote_is_none_when_all_resume_principal_empty(self):
        """If every sommaire has an empty ``resume_principal``, headnote is ``None``."""
        entries = [
            TexteSommaire(id="1", resumePrincipal=None),
            TexteSommaire(id="2", resumePrincipal=""),
        ]
        decision = _make_decision_with(sommaire=entries)

        assert decision.headnote is None

    def test_titrages_returns_empty_list_when_unset(self):
        """A decision without titrages returns ``[]``, not ``None``."""
        decision = _make_decision(None)

        assert decision.titrages == []

    def test_titrages_returns_list_when_populated(self):
        """Titrages list is exposed verbatim."""
        titrages = ["JURINOME000007644451-JURINOME000007645245"]
        decision = _make_decision_with(titrages=titrages)

        assert decision.titrages == titrages


class TestJuriDecisionPublishedInBulletin:
    """Bulletin publication flag on :class:`JuriDecision`."""

    @pytest.mark.parametrize("code", ["P", "B", "R", "T"])
    def test_published_codes_yield_true(self, code):
        """Each known editorial-publication code maps to ``True``."""
        decision = _make_decision_with(typePublicationBulletin=code)

        assert decision.published_in_bulletin is True

    @pytest.mark.parametrize("code", ["p", "b", "r", "t"])
    def test_lowercase_codes_yield_true(self, code):
        """Lowercase variants of known codes are accepted (case-insensitive)."""
        decision = _make_decision_with(typePublicationBulletin=code)

        assert decision.published_in_bulletin is True

    @pytest.mark.parametrize("code", ["N", "n"])
    def test_explicit_n_yields_false(self, code):
        """Explicit ``N`` (non publié) maps to ``False``."""
        decision = _make_decision_with(typePublicationBulletin=code)

        assert decision.published_in_bulletin is False

    def test_missing_flag_yields_false(self):
        """A decision with no ``type_publication_bulletin`` is not published."""
        decision = _make_decision(None)

        assert decision.published_in_bulletin is False

    def test_empty_string_flag_yields_false(self):
        """An empty-string flag is treated as not-published, not as published."""
        decision = _make_decision_with(typePublicationBulletin="")

        assert decision.published_in_bulletin is False

    def test_unknown_code_yields_false(self):
        """An unrecognised code is conservatively reported as not-published."""
        decision = _make_decision_with(typePublicationBulletin="X")

        assert decision.published_in_bulletin is False


class TestJuriDecisionToMarkdown:
    """The Markdown rendering surfaces the headnote and bulletin flag."""

    def test_to_markdown_includes_headnote_when_present(self):
        """The sommaire's ``resume_principal`` appears as a ``**Sommaire**`` line."""
        entries = [TexteSommaire(id="1", resumePrincipal="Forfait jours - Nullité")]
        decision = _make_decision_with(
            id="JURITEXT000037999394",
            titre="Cass. soc., 6 juillet 2016",
            sommaire=entries,
        )

        rendered = decision.to_markdown()

        assert "**Sommaire**: Forfait jours - Nullité" in rendered

    def test_to_markdown_omits_sommaire_block_when_absent(self):
        """No ``**Sommaire**`` line when the decision has no headnote."""
        decision = _make_decision_with(
            id="JURITEXT000037999394",
            titre="Cass. soc., 6 juillet 2016",
        )

        rendered = decision.to_markdown()

        assert "**Sommaire**" not in rendered

    def test_to_markdown_includes_published_in_bulletin_flag(self):
        """A bulletin-published decision is flagged in the Markdown header."""
        decision = _make_decision_with(
            id="JURITEXT000037999394",
            titre="Cass. soc., 6 juillet 2016",
            typePublicationBulletin="P",
        )

        rendered = decision.to_markdown()

        assert "**Publié au Bulletin**: oui" in rendered

    def test_to_markdown_omits_bulletin_flag_when_not_published(self):
        """An unpublished decision does not get a misleading ``oui`` line."""
        decision = _make_decision_with(
            id="JURITEXT000037999394",
            titre="Cass. soc., 6 juillet 2016",
            typePublicationBulletin="N",
        )

        rendered = decision.to_markdown()

        assert "**Publié au Bulletin**" not in rendered
