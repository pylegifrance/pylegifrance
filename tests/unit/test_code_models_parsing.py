"""Unit tests for parsing helpers and branches in pylegifrance.models.code.models:
_to_dict(), _extract_code_name(), Article.from_orm() URL/field branches, and
Article.format_citation()/to_markdown() edge cases.

Uses plain dicts shaped like real Légifrance API JSON responses (camelCase
keys), matching the style of tests/unit/test_code_from_orm.py.
"""

from datetime import datetime
from typing import Any

import pytest

from pylegifrance.models.code.models import Article, Code, _extract_code_name, _to_dict


def _make_article(**fields: Any) -> Article:
    """Build an :class:`Article` from arbitrary fields.

    Routing through ``**fields: Any`` avoids a basedpyright/pydantic
    interop false positive where passing only some keyword arguments
    makes every other (defaulted) field look required.
    """
    return Article(**fields)


# ---------------------------------------------------------------------------
# _to_dict
# ---------------------------------------------------------------------------


class TestToDict:
    def test_dict_input_returned_as_is(self):
        data = {"id": "LEGIARTI1", "num": "1"}
        assert _to_dict(data) is data

    def test_pydantic_model_input_uses_model_dump(self):
        article = _make_article(id="LEGIARTI1", num="1")
        result = _to_dict(article)
        assert isinstance(result, dict)
        assert result["id"] == "LEGIARTI1"
        assert result["number"] == "1"

    def test_plain_object_with_dict_uses_vars(self):
        class Plain:
            def __init__(self):
                self.id = "LEGIARTI1"
                self.num = "1"

        result = _to_dict(Plain())
        assert result == {"id": "LEGIARTI1", "num": "1"}

    def test_object_without_dict_or_model_dump_returns_empty(self):
        class Slotted:
            __slots__ = ()

        result = _to_dict(Slotted())
        assert result == {}


# ---------------------------------------------------------------------------
# _extract_code_name
# ---------------------------------------------------------------------------


class TestExtractCodeName:
    def test_consult_shape_text_titles_list(self):
        article_data = {"textTitles": [{"titre": "Code civil"}]}
        assert _extract_code_name(article_data, {}) == "Code civil"

    def test_text_titles_skips_entries_without_titre(self):
        article_data = {"textTitles": [{"notTitre": "x"}, {"titre": "Code pénal"}]}
        assert _extract_code_name(article_data, {}) == "Code pénal"

    def test_context_titre_txt_list(self):
        article_data = {"context": {"titreTxt": [{"titre": "Code du travail"}]}}
        assert _extract_code_name(article_data, {}) == "Code du travail"

    def test_context_titre_code(self):
        article_data = {"context": {"titreCode": "Code de commerce"}}
        assert _extract_code_name(article_data, {}) == "Code de commerce"

    def test_context_titre(self):
        article_data = {"context": {"titre": "Code rural"}}
        assert _extract_code_name(article_data, {}) == "Code rural"

    def test_top_level_contexte_titre_code(self):
        raw_data = {"contexte": {"titreCode": "Code de la santé publique"}}
        assert _extract_code_name({}, raw_data) == "Code de la santé publique"

    def test_top_level_contexte_titre(self):
        raw_data = {"contexte": {"titre": "Code de l'environnement"}}
        assert _extract_code_name({}, raw_data) == "Code de l'environnement"

    def test_direct_top_level_titre_code(self):
        raw_data = {"titreCode": "Code civil"}
        assert _extract_code_name({}, raw_data) == "Code civil"

    def test_direct_top_level_code_title(self):
        raw_data = {"codeTitle": "Code pénal"}
        assert _extract_code_name({}, raw_data) == "Code pénal"

    def test_direct_top_level_nom_code(self):
        raw_data = {"nomCode": "Code du travail"}
        assert _extract_code_name({}, raw_data) == "Code du travail"

    def test_top_level_context_titre_txt(self):
        raw_data = {"context": {"titreTxt": [{"titre": "Code de commerce"}]}}
        assert _extract_code_name({}, raw_data) == "Code de commerce"

    def test_search_shape_titles_list_with_nature_code(self):
        raw_data = {
            "titles": [
                {"nature": "SECTION", "title": "Not this one"},
                {"nature": "CODE", "title": "Code civil"},
            ]
        }
        assert _extract_code_name({}, raw_data) == "Code civil"

    def test_returns_none_when_nothing_matches(self):
        assert _extract_code_name({}, {}) is None

    def test_priority_text_titles_wins_over_context(self):
        article_data = {
            "textTitles": [{"titre": "Code civil"}],
            "context": {"titreCode": "Should not be used"},
        }
        assert _extract_code_name(article_data, {}) == "Code civil"

    def test_context_titre_txt_entry_not_dict_falls_through(self):
        article_data = {"context": {"titreTxt": ["not-a-dict"], "titreCode": "Code X"}}
        assert _extract_code_name(article_data, {}) == "Code X"


# ---------------------------------------------------------------------------
# Article.from_orm() - URL generation and misc branches
# ---------------------------------------------------------------------------


class TestArticleFromOrmUrl:
    def test_url_generated_from_article_id(self):
        article = Article.from_orm({"id": "LEGIARTI000006419292", "num": "1"})
        assert (
            article.url
            == "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006419292"
        )

    def test_explicit_url_preserved(self):
        article = Article.from_orm(
            {
                "id": "LEGIARTI000006419292",
                "num": "1",
                "url": "https://example.com/custom",
            }
        )
        assert article.url == "https://example.com/custom"

    def test_url_falls_back_to_section_url_when_id_unknown(self):
        article = Article.from_orm({"cid": "LEGITEXT000006070721", "num": "1"})
        assert article.id == "unknown"
        assert (
            article.url
            == "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070721"
        )

    def test_no_url_when_id_unknown_and_no_cid(self):
        article = Article.from_orm({"num": "1"})
        assert article.url is None

    def test_consult_shape_nested_article(self):
        data = {
            "article": {
                "id": "LEGIARTI000006419292",
                "num": "1",
                "texte": "Contenu de l'article",
            }
        }
        article = Article.from_orm(data)
        assert article.id == "LEGIARTI000006419292"
        assert article.content == "Contenu de l'article"

    def test_search_shape_flat_dict(self):
        data = {"id": "LEGIARTI000006419292", "num": "1", "texte": "Contenu"}
        article = Article.from_orm(data)
        assert article.id == "LEGIARTI000006419292"
        assert article.content == "Contenu"

    def test_number_defaults_to_unknown_when_missing(self):
        article = Article.from_orm({"id": "LEGIARTI1"})
        assert article.number == "unknown"

    def test_numero_alias_used_when_num_missing(self):
        article = Article.from_orm({"id": "LEGIARTI1", "numero": "L1121-1"})
        assert article.number == "L1121-1"

    def test_title_from_section_parent_titre_fallback(self):
        article = Article.from_orm(
            {"id": "LEGIARTI1", "num": "1", "sectionParentTitre": "Section title"}
        )
        assert article.title == "Section title"

    def test_title_from_full_sections_titre_fallback(self):
        article = Article.from_orm(
            {"id": "LEGIARTI1", "num": "1", "fullSectionsTitre": "Full section title"}
        )
        assert article.title == "Full section title"

    def test_content_from_values_list_when_texte_missing(self):
        article = Article.from_orm(
            {"id": "LEGIARTI1", "num": "1", "values": ["part1", "part2"]}
        )
        assert article.content == "part1 part2"

    def test_content_from_contenu_fallback(self):
        article = Article.from_orm(
            {"id": "LEGIARTI1", "num": "1", "contenu": "Contenu via contenu"}
        )
        assert article.content == "Contenu via contenu"

    def test_content_from_content_fallback(self):
        article = Article.from_orm(
            {"id": "LEGIARTI1", "num": "1", "content": "Contenu via content"}
        )
        assert article.content == "Contenu via content"

    def test_etat_from_etat_text_fallback(self):
        article = Article.from_orm(
            {"id": "LEGIARTI1", "num": "1", "etatText": "ABROGE"}
        )
        assert article.legal_status == "ABROGE"

    def test_etat_from_raw_data_fallback_when_absent_in_article_data(self):
        data = {
            "article": {"id": "LEGIARTI1", "num": "1"},
            "etatJuridique": "VIGUEUR",
        }
        article = Article.from_orm(data)
        assert article.legal_status == "VIGUEUR"

    def test_legal_status_prefers_version_specific_legalstatus_over_item_level_etat(
        self,
    ):
        """Search responses flatten {**item, **extract}: item-level "etat" is
        the article's overall/global status (same across every historical
        version of that article number), while extract-level "legalStatus" is
        the true per-version status. When both are present -- the real shape
        CODE_ETAT search hits take -- the version-specific one must win, or
        every historical version of an in-force article reports the item's
        "etat" (e.g. all "VIGUEUR") and a VIGUEUR-only filter becomes a no-op.
        """
        article = Article.from_orm(
            {
                "id": "LEGIARTI1",
                "num": "787 B",
                "etat": "VIGUEUR",
                "legalStatus": "MODIFIE",
            }
        )
        assert article.legal_status == "MODIFIE"

    def test_date_version_from_date_debut_fallback(self):
        article = Article.from_orm(
            {"id": "LEGIARTI1", "num": "1", "dateDebut": "2020-01-01T00:00:00"}
        )
        assert article.version_date == datetime(2020, 1, 1)

    def test_date_version_from_raw_data_date_fallback(self):
        data = {
            "article": {"id": "LEGIARTI1", "num": "1"},
            "date": "2020-01-01T00:00:00",
        }
        article = Article.from_orm(data)
        assert article.version_date == datetime(2020, 1, 1)

    def test_cid_from_raw_data_when_absent_in_article_data(self):
        data = {
            "article": {"id": "LEGIARTI1", "num": "1"},
            "cid": "LEGITEXT000006070721",
        }
        article = Article.from_orm(data)
        assert article.cid == "LEGITEXT000006070721"

    def test_texte_html_populated(self):
        article = Article.from_orm(
            {"id": "LEGIARTI1", "num": "1", "texteHtml": "<p>Hi</p>"}
        )
        assert article.content_html == "<p>Hi</p>"

    def test_pydantic_model_input_uses_field_names_not_aliases(self):
        """_to_dict() calls data.model_dump() without by_alias=True, so when
        from_orm() is given an existing Article instance, aliased fields
        (number/title, whose aliases are num/titre) are not found by the
        num/numero and titre/... lookups and fall back to their defaults.
        This documents actual current behaviour, not aspirational round-trip
        behaviour."""
        original = _make_article(id="LEGIARTI1", num="1", titre="Mon titre")
        copy = Article.from_orm(original)
        assert copy.id == "LEGIARTI1"
        assert copy.number == "unknown"
        assert copy.title is None


# ---------------------------------------------------------------------------
# Article.format_citation / to_markdown
# ---------------------------------------------------------------------------


class TestFormatCitation:
    def test_full_citation(self):
        article = _make_article(
            id="LEGIARTI1",
            num="1",
            code_name="Code civil",
            dateVersion="2020-01-01T00:00:00",
        )
        assert article.format_citation() == "Code civil, art. 1 (version du 01/01/2020)"

    def test_citation_without_code_name(self):
        article = _make_article(id="LEGIARTI1", num="123")
        assert article.format_citation() == "art. 123"

    def test_citation_without_version_date(self):
        article = _make_article(id="LEGIARTI1", num="1", code_name="Code civil")
        assert article.format_citation() == "Code civil, art. 1"


class TestToMarkdown:
    def test_to_markdown_with_all_fields(self):
        article = _make_article(
            id="LEGIARTI1",
            num="1",
            code_name="Code civil",
            etatJuridique="VIGUEUR",
            dateVersion="2020-01-01T00:00:00",
            url="https://example.com/a",
            texte="Le contenu brut",
        )
        md = article.to_markdown()
        assert "## Article 1 (Code civil)" in md
        assert "**Statut**: VIGUEUR" in md
        assert "**Référence**: LEGIARTI1" in md
        assert "**Version du**: 01/01/2020" in md
        assert "**URL**: https://example.com/a" in md
        assert "Le contenu brut" in md

    def test_to_markdown_falls_back_to_stripped_html_when_no_text(self):
        article = _make_article(
            id="LEGIARTI1", num="1", texteHtml="<p>Hello <b>world</b></p>"
        )
        md = article.to_markdown()
        assert "Hello world" in md
        assert "<p>" not in md

    def test_to_markdown_minimal_article(self):
        article = _make_article(id="LEGIARTI1", num="1")
        md = article.to_markdown()
        assert "## Article 1" in md
        assert "**Statut**" not in md
        assert "**Référence**: LEGIARTI1" in md


# ---------------------------------------------------------------------------
# Article.parse_date validator
# ---------------------------------------------------------------------------


class TestParseDateValidator:
    def test_parses_iso_string(self):
        article = _make_article(id="1", num="1", dateVersion="2020-01-01T00:00:00")
        assert article.version_date == datetime(2020, 1, 1)

    def test_parses_timestamp_ms(self):
        article = _make_article(id="1", num="1", dateVersion=1577836800000)
        assert article.version_date is not None
        assert article.version_date.year == 2020

    def test_none_stays_none(self):
        article = _make_article(id="1", num="1", dateVersion=None)
        assert article.version_date is None


# ---------------------------------------------------------------------------
# Code.from_orm() - remaining branches not covered by test_code_from_orm.py
# ---------------------------------------------------------------------------


class TestCodeFromOrmAdditional:
    def test_from_orm_with_pydantic_model_input(self):
        original = Code(id="LEGITEXT000006070721", title="Code civil", etat="VIGUEUR")
        copy = Code.from_orm(original)
        assert copy.id == "LEGITEXT000006070721"
        assert copy.title == "Code civil"

    def test_from_orm_titles_without_legitext_prefix_keeps_original_cid(self):
        data = {
            "id": "LEGITEXT000006070721",
            "cid": "ORIGINAL_CID",
            "title": "Code civil",
            "etat": "VIGUEUR",
            "titles": [{"cid": "NOT_LEGITEXT_PREFIXED"}],
        }
        code = Code.from_orm(data)
        assert code.cid == "ORIGINAL_CID"

    def test_from_orm_titles_entries_as_dicts_with_cid_key(self):
        data = {
            "id": "LEGITEXT000006070721",
            "cid": None,
            "titles": [{"cid": "LEGITEXT000006070721"}],
        }
        code = Code.from_orm(data)
        assert code.cid == "LEGITEXT000006070721"

    def test_from_orm_empty_dict_yields_all_none(self):
        code = Code.from_orm({})
        assert code.id is None
        assert code.title is None

    def test_from_orm_plain_object_fallback_uses_getattr(self):
        class Plain:
            id = "LEGITEXT000006070721"
            cid = "LEGITEXT000006070721"
            title = "Code civil"
            etat = "VIGUEUR"
            sections = None
            articles = None

        code = Code.from_orm(Plain())
        assert code.id == "LEGITEXT000006070721"
        assert code.title == "Code civil"


if __name__ == "__main__":
    pytest.main([__file__])
