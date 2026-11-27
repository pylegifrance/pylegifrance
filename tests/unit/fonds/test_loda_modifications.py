"""Unit tests for TexteLoda.get_modified_articles(), get_created_articles(),
format_modifications_report() and the HTML-cleaning helper
_clean_html_for_markdown(), using MagicMocks for the underlying texte model
and real LegifranceClient mocks (so that the `Code` API calls made while
following modification links are exercised end-to-end).
"""

from datetime import datetime
from typing import cast
from unittest.mock import MagicMock

from pylegifrance.fonds.loda import TexteLoda


def _lien(
    link_type: str | None = "MODIFIE",
    article_id: str | None = "LEGIARTI000032930490",
    date_debut_cible: str | None = "2016-07-24",
    text_title: str | None = "LOI n°2015-990 du 6 août 2015",
    article_num: str | None = "53",
    text_cid: str | None = "JORFTEXT000030978561",
):
    lien = MagicMock()
    lien.link_type = link_type
    lien.article_id = article_id
    lien.date_debut_cible = date_debut_cible
    lien.text_title = text_title
    lien.article_num = article_num
    lien.text_cid = text_cid
    return lien


def _article(num="1", content: str | None = "<p>Contenu article</p>", liens=None):
    article = MagicMock()
    article.id = "LEGIARTI000006419292"
    article.num = num
    article.content = content
    article.lst_lien_modification = liens
    return article


def _make_texte_loda(articles=None, client=None) -> TexteLoda:
    texte_mock = MagicMock()
    texte_mock.id = "JORFTEXT000041952174"
    texte_mock.titre = "Loi n° 2020-734"
    texte_mock.etat = "VIGUEUR"
    texte_mock.date_debut_dt = None
    texte_mock.articles = articles

    instance = TexteLoda.__new__(TexteLoda)
    instance._texte = texte_mock
    instance._client = client if client is not None else MagicMock()
    return instance


def _article_response(
    article_id="LEGIARTI000032930490", num="53", texte="Nouveau contenu"
):
    response = MagicMock()
    response.json.return_value = {"id": article_id, "num": num, "texte": texte}
    return response


# ---------------------------------------------------------------------------
# get_modified_articles()
# ---------------------------------------------------------------------------


class TestGetModifiedArticles:
    def test_empty_when_no_articles(self):
        texte = _make_texte_loda(articles=None)
        assert texte.get_modified_articles() == []

    def test_empty_when_article_has_no_links(self):
        texte = _make_texte_loda(articles=[_article(liens=None)])
        assert texte.get_modified_articles() == []

    def test_empty_when_links_attr_missing(self):
        article = MagicMock(spec=["id", "num", "content"])
        texte = _make_texte_loda(articles=[article])
        assert texte.get_modified_articles() == []

    def test_fetches_modified_article_for_modifie_link(self):
        client = MagicMock()
        client.call_api.return_value = _article_response()
        lien = _lien(link_type="MODIFIE")
        texte = _make_texte_loda(articles=[_article(liens=[lien])], client=client)

        result = texte.get_modified_articles()

        assert len(result) == 1
        assert result[0].id == "LEGIARTI000032930490"
        args, _ = client.call_api.call_args
        assert args[0] == "consult/getArticle"
        assert args[1] == {"id": "LEGIARTI000032930490", "date": "2016-07-24"}

    def test_ignores_non_modifie_links(self):
        lien = _lien(link_type="CREE")
        texte = _make_texte_loda(articles=[_article(liens=[lien])])
        assert texte.get_modified_articles() == []

    def test_ignores_link_without_article_id(self):
        lien = _lien(link_type="MODIFIE", article_id=None)
        texte = _make_texte_loda(articles=[_article(liens=[lien])])
        assert texte.get_modified_articles() == []

    def test_ignores_link_without_date_debut_cible(self):
        lien = _lien(link_type="MODIFIE", date_debut_cible=None)
        texte = _make_texte_loda(articles=[_article(liens=[lien])])
        assert texte.get_modified_articles() == []

    def test_continues_when_fetch_raises(self):
        client = MagicMock()
        client.call_api.side_effect = Exception("boom")
        lien = _lien(link_type="MODIFIE")
        texte = _make_texte_loda(articles=[_article(liens=[lien])], client=client)

        assert texte.get_modified_articles() == []

    def test_multiple_articles_and_links(self):
        client = MagicMock()
        client.call_api.return_value = _article_response()
        lien1 = _lien(link_type="MODIFIE", article_id="LEGIARTI000001")
        lien2 = _lien(link_type="MODIFIE", article_id="LEGIARTI000002")
        texte = _make_texte_loda(
            articles=[_article(liens=[lien1]), _article(liens=[lien2])],
            client=client,
        )

        result = texte.get_modified_articles()
        assert len(result) == 2


# ---------------------------------------------------------------------------
# get_created_articles()
# ---------------------------------------------------------------------------


class TestGetCreatedArticles:
    def test_empty_when_no_articles(self):
        texte = _make_texte_loda(articles=None)
        assert texte.get_created_articles() == []

    def test_empty_when_article_has_no_links(self):
        texte = _make_texte_loda(articles=[_article(liens=None)])
        assert texte.get_created_articles() == []

    def test_fetches_created_article_for_cree_link(self):
        client = MagicMock()
        client.call_api.return_value = _article_response(num="53-1")
        lien = _lien(link_type="CREE", date_debut_cible="2016-07-24")
        texte = _make_texte_loda(articles=[_article(liens=[lien])], client=client)

        result = texte.get_created_articles()

        assert len(result) == 1
        args, _ = client.call_api.call_args
        assert args[1] == {"id": "LEGIARTI000032930490", "date": "2016-07-24"}

    def test_fetches_created_article_without_date_fetches_current_version(self):
        """Regression test for a bug where a creation link without
        date_debut_cible made get_created_articles() append the unexecuted
        ArticleFetcher builder instead of actually fetching the article's
        current version (see _fetch_article_with_date docstring: "ou None
        pour la version courante"). Fixed in loda.py:440-441.
        """
        client = MagicMock()
        client.call_api.return_value = _article_response()
        lien = _lien(link_type="CREATION", date_debut_cible=None)
        texte = _make_texte_loda(articles=[_article(liens=[lien])], client=client)

        result = texte.get_created_articles()

        assert len(result) == 1
        # Must be a real, fetched Article with usable content, not the
        # unexecuted ArticleFetcher builder.
        assert result[0].content == "Nouveau contenu"
        args, _ = client.call_api.call_args
        assert args[0] == "consult/getArticle"
        assert args[1]["id"] == "LEGIARTI000032930490"
        # No explicit date was available, so today's date must be used.
        assert args[1]["date"] == datetime.now().strftime("%Y-%m-%d")

    def test_ignores_non_creation_links(self):
        lien = _lien(link_type="MODIFIE")
        texte = _make_texte_loda(articles=[_article(liens=[lien])])
        assert texte.get_created_articles() == []

    def test_ignores_link_without_article_id(self):
        lien = _lien(link_type="CREE", article_id=None)
        texte = _make_texte_loda(articles=[_article(liens=[lien])])
        assert texte.get_created_articles() == []

    def test_continues_when_fetch_raises(self):
        client = MagicMock()
        client.call_api.side_effect = Exception("boom")
        lien = _lien(link_type="CREE")
        texte = _make_texte_loda(articles=[_article(liens=[lien])], client=client)

        assert texte.get_created_articles() == []

    def test_accepts_all_creation_link_type_spellings(self):
        client = MagicMock()
        client.call_api.return_value = _article_response()
        for link_type in ["CREE", "CREATION", "CRÉÉ", "CRÉATION"]:
            lien = _lien(link_type=link_type)
            texte = _make_texte_loda(articles=[_article(liens=[lien])], client=client)
            assert len(texte.get_created_articles()) == 1


# ---------------------------------------------------------------------------
# format_modifications_report()
# ---------------------------------------------------------------------------


class TestFormatModificationsReport:
    def test_no_articles_returns_placeholder(self):
        texte = _make_texte_loda(articles=None)
        assert texte.format_modifications_report() == "Aucun impact disponible."

    def test_articles_without_modification_links_report_no_impact(self):
        texte = _make_texte_loda(articles=[_article(liens=None)])
        report = texte.format_modifications_report()
        assert "Aucun impact trouvé dans cette loi." in report
        assert "# Impact de cette loi" in report

    def test_header_includes_titre_and_etat(self):
        texte = _make_texte_loda(articles=[_article(liens=None)])
        report = texte.format_modifications_report()
        assert "**Titre**: Loi n° 2020-734" in report
        assert "**Statut**: VIGUEUR" in report
        assert "Non spécifiée" in report  # no date_debut_dt set

    def test_modification_link_produces_summary_and_section(self):
        client = MagicMock()
        client.call_api.return_value = _article_response(
            num="53", texte="Nouveau texte"
        )
        lien = _lien(link_type="MODIFIE")
        texte = _make_texte_loda(articles=[_article(liens=[lien])], client=client)

        report = texte.format_modifications_report()

        assert "### Modification 1:" in report
        assert "**Citation**:" in report
        assert "**Consulter**:" in report
        assert "Nouveau contenu" in report
        assert "- **Modifications**: 1 article(s)" in report
        assert "- **Créations**: 0 article(s)" in report
        assert "- **Abrogations**: 0 article(s)" in report
        assert "- **Impact total**: 1 article(s)" in report

    def test_creation_link_produces_summary_and_section(self):
        client = MagicMock()
        client.call_api.return_value = _article_response(num="53-1")
        lien = _lien(link_type="CREE")
        texte = _make_texte_loda(articles=[_article(liens=[lien])], client=client)

        report = texte.format_modifications_report()

        assert "### Création 1:" in report
        assert "- **Créations**: 1 article(s)" in report

    def test_abrogation_link_produces_section(self):
        lien = _lien(link_type="ABROGE")
        texte = _make_texte_loda(articles=[_article(liens=[lien])])

        report = texte.format_modifications_report()

        assert "### Abrogation 1:" in report
        assert "**Article abrogé**:" in report
        assert "**Date d'abrogation**:" in report
        assert "**Code source**:" in report
        assert "- **Abrogations**: 1 article(s)" in report

    def test_other_link_type_produces_generic_section(self):
        lien = _lien(link_type="DISJOINT")
        texte = _make_texte_loda(articles=[_article(liens=[lien])])

        report = texte.format_modifications_report()

        assert "### Disjoint 1:" in report
        assert "**Type d'action**: DISJOINT" in report

    def test_article_content_included_in_report(self):
        lien = _lien(link_type="ABROGE")
        texte = _make_texte_loda(
            articles=[_article(content="<p>Texte de loi</p>", liens=[lien])]
        )

        report = texte.format_modifications_report()
        assert "Texte de loi" in report
        assert "**Contenu de l'article de loi**:" in report

    def test_article_without_content_omits_content_block(self):
        lien = _lien(link_type="ABROGE")
        texte = _make_texte_loda(articles=[_article(content=None, liens=[lien])])

        report = texte.format_modifications_report()
        assert "**Contenu de l'article de loi**" not in report

    def test_creation_without_date_fetches_current_version_content(self):
        """Regression test: a CREE link with no date_debut_cible must still
        produce real article content in the report (current version),
        rather than silently failing with "**Erreur**" because
        _fetch_article_from_link returned an unexecuted ArticleFetcher
        instead of calling .at(). Fixed in loda.py:633-643.
        """
        client = MagicMock()
        client.call_api.return_value = _article_response(
            num="53-1", texte="Contenu de l'article créé"
        )
        lien = _lien(link_type="CREE", date_debut_cible=None)
        texte = _make_texte_loda(articles=[_article(liens=[lien])], client=client)

        report = texte.format_modifications_report()

        assert "**Erreur**" not in report
        assert "Contenu de l'article créé" in report
        args, _ = client.call_api.call_args
        assert args[1]["date"] == datetime.now().strftime("%Y-%m-%d")

    def test_fetch_error_is_reported_inline(self):
        client = MagicMock()
        client.call_api.side_effect = Exception("network error")
        lien = _lien(link_type="MODIFIE")
        texte = _make_texte_loda(articles=[_article(liens=[lien])], client=client)

        report = texte.format_modifications_report()
        assert "**Erreur**: Impossible de récupérer le contenu" in report

    def test_article_content_absent_when_fetched_article_has_none(self):
        client = MagicMock()
        response = MagicMock()
        response.json.return_value = {"id": "LEGIARTI000032930490", "num": "53"}
        client.call_api.return_value = response
        lien = _lien(link_type="MODIFIE")
        texte = _make_texte_loda(articles=[_article(liens=[lien])], client=client)

        report = texte.format_modifications_report()
        assert "**Nouveau contenu**" not in report

    def test_multiple_links_each_followed_by_separator(self):
        lien1 = _lien(link_type="ABROGE", article_num="1")
        lien2 = _lien(link_type="ABROGE", article_num="2")
        texte = _make_texte_loda(articles=[_article(liens=[lien1, lien2])])

        report = texte.format_modifications_report()
        assert report.count("---") >= 2


# ---------------------------------------------------------------------------
# _clean_html_for_markdown()
# ---------------------------------------------------------------------------


class TestCleanHtmlForMarkdown:
    def _texte(self):
        return _make_texte_loda(articles=None)

    def test_empty_string_for_falsy_input(self):
        assert self._texte()._clean_html_for_markdown("") == ""
        # _clean_html_for_markdown is declared as taking a plain `str`, but
        # its implementation explicitly tolerates a falsy/None value at
        # runtime (`if not html_content: return ""`); the cast documents
        # that this is a deliberate exercise of that defensive branch.
        assert self._texte()._clean_html_for_markdown(cast(str, None)) == ""

    def test_strips_internal_legifrance_links(self):
        html = (
            '<a href="/affichCodeArticle.do?cidTexte=LEGITEXT1&idArticle=LEGIARTI1">'
            "Article 1</a>"
        )
        cleaned = self._texte()._clean_html_for_markdown(html)
        assert cleaned == "Article 1"

    def test_converts_external_links_to_markdown(self):
        html = '<a href="https://example.com/page">External</a>'
        cleaned = self._texte()._clean_html_for_markdown(html)
        assert cleaned == "[External](https://example.com/page)"

    def test_strips_legifrance_gouv_fr_http_links_without_markdown(self):
        html = '<a href="https://www.legifrance.gouv.fr/some/path">Lien</a>'
        cleaned = self._texte()._clean_html_for_markdown(html)
        assert cleaned == "Lien"

    def test_br_converted_to_newline(self):
        html = "Ligne 1<br/>Ligne 2"
        cleaned = self._texte()._clean_html_for_markdown(html)
        assert "Ligne 1\nLigne 2" in cleaned

    def test_paragraphs_separated(self):
        html = "<p>Un</p><p>Deux</p>"
        cleaned = self._texte()._clean_html_for_markdown(html)
        assert "Un" in cleaned and "Deux" in cleaned

    def test_blockquote_prefixed(self):
        html = "<blockquote>Citation</blockquote>"
        cleaned = self._texte()._clean_html_for_markdown(html)
        assert "> Citation" in cleaned

    def test_url_params_removed(self):
        html = '<a href="https://example.com/page?cidTexte=FOO&other=1">Link</a>'
        cleaned = self._texte()._clean_html_for_markdown(html)
        assert "cidTexte" not in cleaned

    def test_handles_non_dict_url_encoded_content(self):
        html = "%3Cp%3EEncoded%3C%2Fp%3E"
        cleaned = self._texte()._clean_html_for_markdown(html)
        assert "Encoded" in cleaned

    def test_excessive_newlines_collapsed(self):
        html = "<p>Un</p>\n\n\n\n<p>Deux</p>"
        cleaned = self._texte()._clean_html_for_markdown(html)
        assert "\n\n\n" not in cleaned
