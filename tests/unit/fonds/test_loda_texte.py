"""Unit tests for TexteLoda properties and version-navigation methods
(.at(), .latest(), .versions()), using a MagicMock for the underlying
TexteLodaModel (matching the pattern in test_to_markdown.py).
"""

from datetime import datetime
from typing import cast
from unittest.mock import MagicMock, patch

import pytest

from pylegifrance.fonds.loda import TexteLoda


def _make_texte_loda(**overrides) -> TexteLoda:
    texte_mock = MagicMock()
    texte_mock.id = "LEGITEXT000041952174"
    texte_mock.cid = "LEGITEXT000041952174"
    texte_mock.nor = "MTRD2011622L"
    texte_mock.titre = "Loi n° 2020-734"
    texte_mock.titre_long = "Loi n° 2020-734 du 17 juin 2020 relative à..."
    texte_mock.date_debut_dt = datetime(2020, 6, 17)
    texte_mock.date_fin_dt = None
    texte_mock.etat = "VIGUEUR"
    texte_mock.last_update_dt = datetime(2020, 6, 18)
    texte_mock.consult_response = None
    texte_mock.texte_html = None
    texte_mock.articles = None
    texte_mock.sections = None
    for key, value in overrides.items():
        setattr(texte_mock, key, value)

    instance = TexteLoda.__new__(TexteLoda)
    instance._texte = texte_mock
    instance._client = MagicMock()
    return instance


# ---------------------------------------------------------------------------
# Simple properties
# ---------------------------------------------------------------------------


class TestProperties:
    def test_id_present(self):
        assert _make_texte_loda().id == "LEGITEXT000041952174"

    def test_id_none_when_falsy(self):
        assert _make_texte_loda(id=None).id is None
        assert _make_texte_loda(id="").id is None

    def test_cid_present(self):
        texte = _make_texte_loda()
        assert str(texte.cid) == "LEGITEXT000041952174"

    def test_cid_none_when_falsy(self):
        assert _make_texte_loda(cid=None).cid is None

    def test_nor_present(self):
        texte = _make_texte_loda()
        assert str(texte.nor) == "MTRD2011622L"

    def test_nor_none_when_falsy(self):
        assert _make_texte_loda(nor=None).nor is None

    def test_cid_returns_none_instead_of_raising_on_malformed_value(self):
        """A truthy but malformed cid from a real API response must degrade
        to None (the property's own documented contract), not crash a
        caller like to_markdown() that reads it unconditionally."""
        assert _make_texte_loda(cid="not-a-real-cid").cid is None

    def test_nor_returns_none_instead_of_raising_on_malformed_value(self):
        assert _make_texte_loda(nor="not-a-real-nor").nor is None

    def test_titre(self):
        assert _make_texte_loda().titre == "Loi n° 2020-734"

    def test_titre_long(self):
        titre_long = _make_texte_loda().titre_long
        assert titre_long is not None
        assert "relative à" in titre_long

    def test_date_debut(self):
        assert _make_texte_loda().date_debut == datetime(2020, 6, 17)

    def test_date_fin_none(self):
        assert _make_texte_loda().date_fin is None

    def test_etat(self):
        assert _make_texte_loda().etat == "VIGUEUR"

    def test_last_update(self):
        assert _make_texte_loda().last_update == datetime(2020, 6, 18)

    def test_date_publication_none_without_consult_response(self):
        assert _make_texte_loda(consult_response=None).date_publication is None

    def test_date_publication_from_consult_response(self):
        consult_response = MagicMock()
        consult_response.date_parution = datetime(2020, 6, 18)
        texte = _make_texte_loda(consult_response=consult_response)
        assert texte.date_publication == datetime(2020, 6, 18)

    def test_sections_property(self):
        sections = [MagicMock()]
        assert _make_texte_loda(sections=sections).sections is sections

    def test_articles_property(self):
        articles = [MagicMock()]
        assert _make_texte_loda(articles=articles).articles is articles

    def test_to_dict_delegates_to_model_dump(self):
        texte = _make_texte_loda()
        # `_texte` is statically typed as the real model, but `_make_texte_loda`
        # actually assigns a MagicMock to it; the cast reflects that reality
        # so we can configure the mocked `model_dump()` return value.
        texte_mock = cast(MagicMock, texte._texte)
        texte_mock.model_dump.return_value = {"id": "x"}
        assert texte.to_dict() == {"id": "x"}

    def test_repr(self):
        texte = _make_texte_loda()
        assert (
            repr(texte) == "TexteLoda(id=LEGITEXT000041952174, titre=Loi n° 2020-734)"
        )


# ---------------------------------------------------------------------------
# texte_html fallback extraction
# ---------------------------------------------------------------------------


class TestTexteHtmlFallback:
    def test_returns_texte_html_directly_when_present(self):
        texte = _make_texte_loda(texte_html="<p>Direct HTML</p>")
        assert texte.texte_html == "<p>Direct HTML</p>"

    def test_none_when_no_content_anywhere(self):
        texte = _make_texte_loda(texte_html=None, articles=None, sections=None)
        assert texte.texte_html is None

    def test_extracts_from_root_articles(self):
        article = MagicMock()
        article.content = "<p>Article content</p>"
        texte = _make_texte_loda(texte_html=None, articles=[article], sections=None)
        assert texte.texte_html == "<p>Article content</p>"

    def test_skips_articles_without_content(self):
        article = MagicMock()
        article.content = None
        texte = _make_texte_loda(texte_html=None, articles=[article], sections=None)
        assert texte.texte_html is None

    def test_extracts_from_sections_with_title_and_articles(self):
        article = MagicMock()
        article.content = "<p>Section article</p>"
        section = MagicMock()
        section.title = "Titre section"
        section.articles = [article]
        texte = _make_texte_loda(texte_html=None, articles=None, sections=[section])

        html = texte.texte_html
        assert html is not None
        assert "<h2>Titre section</h2>" in html
        assert "<p>Section article</p>" in html

    def test_section_without_title_or_articles(self):
        section = MagicMock()
        section.title = None
        section.articles = None
        texte = _make_texte_loda(texte_html=None, articles=None, sections=[section])
        assert texte.texte_html is None

    def test_combines_articles_and_sections(self):
        root_article = MagicMock()
        root_article.content = "<p>Root</p>"
        section_article = MagicMock()
        section_article.content = "<p>Section</p>"
        section = MagicMock()
        section.title = None
        section.articles = [section_article]

        texte = _make_texte_loda(
            texte_html=None, articles=[root_article], sections=[section]
        )
        html = texte.texte_html
        assert html is not None
        assert "<p>Root</p>" in html
        assert "<p>Section</p>" in html


# ---------------------------------------------------------------------------
# texte_brut
# ---------------------------------------------------------------------------


class TestTexteBrut:
    def test_none_when_no_html(self):
        assert _make_texte_loda(texte_html=None).texte_brut is None

    def test_strips_tags_and_preserves_breaks(self):
        html = "<p>Premier paragraphe.</p><p>Second paragraphe.</p>"
        texte = _make_texte_loda(texte_html=html)
        brut = texte.texte_brut
        assert brut is not None
        assert "<p>" not in brut
        assert "Premier paragraphe." in brut
        assert "Second paragraphe." in brut

    def test_br_converted_to_newline(self):
        html = "Ligne 1<br/>Ligne 2"
        texte = _make_texte_loda(texte_html=html)
        brut = texte.texte_brut
        assert brut is not None
        assert "Ligne 1\nLigne 2" in brut

    def test_blockquote_and_headings_spaced(self):
        html = "<h1>Titre</h1><blockquote>Citation</blockquote>"
        texte = _make_texte_loda(texte_html=html)
        brut = texte.texte_brut
        assert brut is not None
        assert "Titre" in brut
        assert "Citation" in brut

    def test_returns_none_for_whitespace_only_result(self):
        html = "<p>   </p>"
        texte = _make_texte_loda(texte_html=html)
        assert texte.texte_brut is None


# ---------------------------------------------------------------------------
# .at() / .latest() / .versions()
# ---------------------------------------------------------------------------


class TestAt:
    def test_at_with_datetime(self):
        texte = _make_texte_loda()
        expected = MagicMock()
        with patch("pylegifrance.fonds.loda.Loda") as loda_cls:
            loda_cls.return_value.fetch_version_at.return_value = expected
            result = texte.at(datetime(2021, 1, 1))

        loda_cls.return_value.fetch_version_at.assert_called_once()
        call_args = loda_cls.return_value.fetch_version_at.call_args[0]
        assert call_args[0] == "LEGITEXT000041952174"
        assert call_args[1] == datetime(2021, 1, 1).isoformat()
        assert result is expected

    def test_at_with_valid_iso_string(self):
        texte = _make_texte_loda()
        with patch("pylegifrance.fonds.loda.Loda") as loda_cls:
            loda_cls.return_value.fetch_version_at.return_value = None
            texte.at("2021-01-01")

        call_args = loda_cls.return_value.fetch_version_at.call_args[0]
        assert call_args[1] == "2021-01-01"

    def test_at_with_invalid_string_raises(self):
        texte = _make_texte_loda()
        with pytest.raises(ValueError):
            texte.at("not-a-date")

    def test_at_raises_when_id_is_none(self):
        texte = _make_texte_loda(id=None)
        with pytest.raises(ValueError):
            texte.at("2021-01-01")


class TestLatest:
    def test_latest_delegates_to_loda_fetch(self):
        texte = _make_texte_loda()
        expected = MagicMock()
        with patch("pylegifrance.fonds.loda.Loda") as loda_cls:
            loda_cls.return_value.fetch.return_value = expected
            result = texte.latest()

        loda_cls.return_value.fetch.assert_called_once_with("LEGITEXT000041952174")
        assert result is expected

    def test_latest_raises_when_id_is_none(self):
        texte = _make_texte_loda(id=None)
        with pytest.raises(ValueError):
            texte.latest()


class TestVersions:
    def test_versions_delegates_to_loda_fetch_versions(self):
        texte = _make_texte_loda()
        expected = [MagicMock(), MagicMock()]
        with patch("pylegifrance.fonds.loda.Loda") as loda_cls:
            loda_cls.return_value.fetch_versions.return_value = expected
            result = texte.versions()

        loda_cls.return_value.fetch_versions.assert_called_once_with(
            "LEGITEXT000041952174"
        )
        assert result is expected

    def test_versions_returns_empty_list_when_id_is_none(self):
        texte = _make_texte_loda(id=None)
        assert texte.versions() == []
