"""Unit tests for .to_markdown() on Article, JuriDecision and TexteLoda."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.juri import JuriDecision
from pylegifrance.fonds.loda import TexteLoda as DomainTexteLoda
from pylegifrance.models.code.models import Article


# ---------------------------------------------------------------------------
# Article.to_markdown()
# ---------------------------------------------------------------------------


class TestArticleToMarkdown:
    def _make_article(self, **kwargs) -> Article:
        defaults = {
            "id": "LEGIARTI000006419292",
            "number": "L1121-1",
            "code_name": "Code du travail",
            "legal_status": "VIGUEUR",
            "content": "Nul ne peut apporter aux droits des personnes...",
            "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006419292",
        }
        defaults.update(kwargs)
        return Article(**defaults)

    def test_heading_includes_number_and_code_name(self):
        md = self._make_article().to_markdown()
        assert "## Article L1121-1 (Code du travail)" in md

    def test_heading_without_code_name(self):
        md = self._make_article(code_name=None).to_markdown()
        assert "## Article L1121-1" in md
        assert "(None)" not in md

    def test_metadata_statut(self):
        md = self._make_article().to_markdown()
        assert "**Statut**: VIGUEUR" in md

    def test_metadata_reference(self):
        md = self._make_article().to_markdown()
        assert "**Référence**: LEGIARTI000006419292" in md

    def test_metadata_url(self):
        md = self._make_article().to_markdown()
        assert "**URL**: https://www.legifrance.gouv.fr" in md

    def test_version_date_formatted(self):
        article = self._make_article(version_date=datetime(2020, 1, 1))
        md = article.to_markdown()
        assert "**Version du**: 01/01/2020" in md

    def test_content_in_body(self):
        md = self._make_article().to_markdown()
        assert "Nul ne peut apporter aux droits des personnes" in md

    def test_html_fallback_when_no_plain_content(self):
        article = self._make_article(
            content=None,
            content_html="<p>Plain text from HTML</p>",
        )
        md = article.to_markdown()
        assert "Plain text from HTML" in md
        assert "<p>" not in md

    def test_empty_body_when_no_content(self):
        article = self._make_article(content=None, content_html=None)
        md = article.to_markdown()
        assert "## Article L1121-1" in md

    def test_no_status_when_none(self):
        md = self._make_article(legal_status=None).to_markdown()
        assert "**Statut**" not in md

    def test_returns_string(self):
        assert isinstance(self._make_article().to_markdown(), str)


# ---------------------------------------------------------------------------
# JuriDecision._extract_plain_text() and to_markdown()
# ---------------------------------------------------------------------------


def _make_juri_decision(**attrs) -> JuriDecision:
    """Build a JuriDecision around a MagicMock decision model."""
    decision_mock = MagicMock()
    decision_mock.id = attrs.get("id", "JURITEXT000027546700")
    decision_mock.texte = attrs.get("texte", None)
    decision_mock.texte_html = attrs.get("texte_html", None)
    decision_mock.titre = attrs.get("titre", "Arrêt de la Chambre sociale")
    decision_mock.solution = attrs.get("solution", "REJET")
    decision_mock.formation = attrs.get("formation", "Chambre sociale")
    decision_mock.juridiction = attrs.get("juridiction", "Cour de cassation")
    decision_mock.num = attrs.get("num", "18-26.218")
    decision_mock.ecli = attrs.get("ecli", "ECLI:FR:CCASS:2020:SO00123")
    decision_mock.date_texte = attrs.get("date_texte", None)
    decision_mock.liens = []
    decision_mock.nor = None
    decision_mock.id_eli = None
    return JuriDecision(decision=decision_mock, client=MagicMock())


class TestJuriDecisionExtractPlainText:
    def test_returns_texte_when_available(self):
        jd = _make_juri_decision(texte="Plain text content.")
        assert jd._extract_plain_text() == "Plain text content."

    def test_strips_html_when_no_texte(self):
        jd = _make_juri_decision(
            texte=None,
            texte_html="<p>Attendu que <strong>la loi</strong> dispose.</p>",
        )
        result = jd._extract_plain_text()
        assert result is not None
        assert "Attendu que" in result
        assert "<p>" not in result
        assert "<strong>" not in result

    def test_returns_none_when_both_absent(self):
        jd = _make_juri_decision(texte=None, texte_html=None)
        assert jd._extract_plain_text() is None


class TestJuriDecisionToMarkdown:
    def test_heading_includes_jurisdiction_and_formation(self):
        md = _make_juri_decision().to_markdown()
        assert "Cour de cassation" in md
        assert "Chambre sociale" in md

    def test_heading_with_date(self):
        jd = _make_juri_decision(date_texte=datetime(2020, 3, 4))
        md = jd.to_markdown()
        assert "04/03/2020" in md

    def test_solution_in_metadata(self):
        md = _make_juri_decision().to_markdown()
        assert "**Solution**: REJET" in md

    def test_ecli_in_metadata(self):
        md = _make_juri_decision().to_markdown()
        assert "**ECLI**: ECLI:FR:CCASS:2020:SO00123" in md

    def test_reference_in_metadata(self):
        md = _make_juri_decision().to_markdown()
        assert "**Référence**: JURITEXT000027546700" in md

    def test_url_in_metadata(self):
        md = _make_juri_decision().to_markdown()
        assert "**URL**: https://www.legifrance.gouv.fr/juri/id/JURITEXT000027546700" in md

    def test_plain_text_body_from_texte(self):
        jd = _make_juri_decision(texte="Attendu que la demande est rejetée.")
        md = jd.to_markdown()
        assert "Attendu que la demande est rejetée." in md

    def test_plain_text_body_from_html(self):
        jd = _make_juri_decision(
            texte=None,
            texte_html="<p>Vu les articles L1121-1</p>",
        )
        md = jd.to_markdown()
        assert "Vu les articles L1121-1" in md
        assert "<p>" not in md

    def test_fallback_heading_when_no_jurisdiction(self):
        jd = _make_juri_decision(juridiction=None, formation=None)
        md = jd.to_markdown()
        assert md.startswith("## ")

    def test_returns_string(self):
        assert isinstance(_make_juri_decision().to_markdown(), str)


# ---------------------------------------------------------------------------
# TexteLoda.to_markdown()
# ---------------------------------------------------------------------------


def _make_texte_loda(
    titre="Loi n° 2020-734",
    id_="LEGITEXT000041952174",
    etat="VIGUEUR",
    nor=None,
    date_debut=None,
    texte_html=None,
) -> DomainTexteLoda:
    """Build a DomainTexteLoda backed by a MagicMock model."""
    texte_mock = MagicMock()
    texte_mock.date_debut_dt = date_debut or datetime(2020, 6, 17)
    texte_mock.texte_html = texte_html
    texte_mock.sections = None
    texte_mock.articles = None
    texte_mock.nor = nor
    texte_mock.titre = titre
    texte_mock.id = id_
    texte_mock.etat = etat

    loda = DomainTexteLoda.__new__(DomainTexteLoda)
    loda._texte = texte_mock
    loda._client = MagicMock()
    loda._code_client = None
    return loda


class TestTexteLodaToMarkdown:
    def test_heading_uses_titre(self):
        md = _make_texte_loda().to_markdown()
        assert "## Loi n° 2020-734" in md

    def test_heading_falls_back_to_id(self):
        md = _make_texte_loda(titre=None).to_markdown()
        assert "## LEGITEXT000041952174" in md

    def test_statut_in_metadata(self):
        md = _make_texte_loda().to_markdown()
        assert "**Statut**: VIGUEUR" in md

    def test_reference_in_metadata(self):
        md = _make_texte_loda().to_markdown()
        assert "**Référence**: LEGITEXT000041952174" in md

    def test_date_formatted(self):
        md = _make_texte_loda(date_debut=datetime(2020, 6, 17)).to_markdown()
        assert "**En vigueur depuis**: 17/06/2020" in md

    def test_url_in_metadata(self):
        md = _make_texte_loda().to_markdown()
        assert "**URL**: https://www.legifrance.gouv.fr/loda/id/LEGITEXT000041952174" in md

    def test_nor_in_metadata_when_present(self):
        md = _make_texte_loda(nor="MTRD2011622L").to_markdown()
        assert "**NOR**: MTRD2011622L" in md

    def test_nor_absent_when_none(self):
        md = _make_texte_loda(nor=None).to_markdown()
        assert "**NOR**" not in md

    def test_html_body_cleaned(self):
        md = _make_texte_loda(texte_html="<p>Contenu de la loi.</p>").to_markdown()
        assert "Contenu de la loi." in md
        assert "<p>" not in md

    def test_placeholder_when_no_html(self):
        md = _make_texte_loda(texte_html=None).to_markdown()
        assert "`.latest()`" in md or "`.at(date)`" in md

    def test_returns_string(self):
        assert isinstance(_make_texte_loda().to_markdown(), str)
