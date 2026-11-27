"""Unit tests for CodeSearchBuilder normalization and post-filtering."""

import json
from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.code import CodeSearchBuilder, _normalize_article_number
from pylegifrance.models.code.enum import NomCode
from pylegifrance.models.constants import EtatJuridique
from pylegifrance.models.generated.model import TypePagination

# ---------------------------------------------------------------------------
# _normalize_article_number
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("L. 1121-1", "L1121-1"),
        ("R. 4614-2", "R4614-2"),
        ("D. 1-1", "D1-1"),
        ("LO. 141-1", "LO141-1"),
        ("L1121-1", "L1121-1"),
        ("R4614-2", "R4614-2"),
        ("1234", "1234"),
        ("  L. 1121-1  ", "L1121-1"),  # leading/trailing whitespace stripped
        ("A. 1", "A1"),
    ],
)
def test_normalize_article_number(raw, expected):
    assert _normalize_article_number(raw) == expected


def test_normalize_article_number_already_normalized_unchanged():
    """Numbers already in API format pass through without modification."""
    assert _normalize_article_number("L1121-1") == "L1121-1"


# ---------------------------------------------------------------------------
# CodeSearchBuilder.article_number() normalization
# ---------------------------------------------------------------------------


def test_article_number_builder_normalizes_french_format():
    """article_number("L. 1121-1") stores the normalized form "L1121-1"."""
    client = MagicMock()
    builder = CodeSearchBuilder(client, "CODE_ETAT")
    builder.article_number("L. 1121-1")

    # Inspect the stored champ
    assert len(builder._champs) == 1
    champ = builder._champs[0]
    assert len(champ.criteres) == 1
    assert champ.criteres[0].valeur == "L1121-1"


def test_article_number_builder_leaves_already_normalized_unchanged():
    client = MagicMock()
    builder = CodeSearchBuilder(client, "CODE_ETAT")
    builder.article_number("L1121-1")

    champ = builder._champs[0]
    assert champ.criteres[0].valeur == "L1121-1"


# ---------------------------------------------------------------------------
# CodeSearchBuilder execute() legal status post-filter
# ---------------------------------------------------------------------------


def _mock_search_response(articles: list[dict]) -> MagicMock:
    """Return a mock response object wrapping the given article dicts."""
    body = {
        "pageNumber": 1,
        "pageSize": 100,
        "totalResults": len(articles),
        "results": articles,
    }
    mock = MagicMock()
    mock.text = json.dumps(body)
    return mock


def _vigueur_article(id_: str, num: str) -> dict:
    return {"id": id_, "num": num, "etatJuridique": "VIGUEUR"}


def _abroge_article(id_: str, num: str) -> dict:
    return {"id": id_, "num": num, "etatJuridique": "ABROGE"}


class TestPostFilter:
    def _builder_with_vigueur(self, client: MagicMock) -> CodeSearchBuilder:
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.in_code(NomCode.CDT)
        builder.with_legal_status([EtatJuridique.VIGUEUR])
        return builder

    def test_removes_abroge_articles(self):
        client = MagicMock()
        client.call_api.return_value = _mock_search_response(
            [
                _vigueur_article("LEGIARTI000001", "L1121-1"),
                _abroge_article("LEGIARTI000002", "L1121-1"),
            ]
        )

        results = self._builder_with_vigueur(client).execute()

        assert len(results) == 1
        assert results[0].legal_status == "VIGUEUR"
        assert results[0].id == "LEGIARTI000001"

    def test_keeps_all_vigueur_articles(self):
        client = MagicMock()
        client.call_api.return_value = _mock_search_response(
            [
                _vigueur_article("LEGIARTI000001", "L1121-1"),
                _vigueur_article("LEGIARTI000002", "L1221-1"),
            ]
        )

        results = self._builder_with_vigueur(client).execute()

        assert len(results) == 2

    def test_no_post_filter_when_status_not_set(self):
        """Without with_legal_status(), mixed-status articles all pass through."""
        client = MagicMock()
        client.call_api.return_value = _mock_search_response(
            [
                _vigueur_article("LEGIARTI000001", "L1121-1"),
                _abroge_article("LEGIARTI000002", "L1121-1"),
            ]
        )

        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.in_code(NomCode.CDT)
        results = builder.execute()

        assert len(results) == 2

    def test_empty_result_when_all_filtered_out(self):
        client = MagicMock()
        client.call_api.return_value = _mock_search_response(
            [_abroge_article("LEGIARTI000001", "L1121-1")]
        )

        results = self._builder_with_vigueur(client).execute()

        assert results == []

    def test_stored_requested_statuses_set(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.in_code(NomCode.CDT)
        builder.with_legal_status([EtatJuridique.VIGUEUR])

        assert builder._requested_statuses == [EtatJuridique.VIGUEUR]

    def test_requested_statuses_none_before_with_legal_status(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")

        assert builder._requested_statuses is None


# ---------------------------------------------------------------------------
# CodeSearchBuilder pagination: the search API only returns a handful of
# per-article version "extracts" per matched text under DEFAUT pagination
# (surfaced via a "moreArticlesCount" counter on the item), capped well below
# an article's real version count. A legal-status filter needs the *true*
# current version to actually be among the fetched extracts, or the filter
# silently finds nothing to keep. typePagination=ARTICLE makes the API
# paginate over extracts instead of over matched texts.
# ---------------------------------------------------------------------------


class TestArticlePagination:
    def test_with_legal_status_switches_to_article_pagination(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.in_code(NomCode.CDT)

        builder.with_legal_status([EtatJuridique.VIGUEUR])

        assert builder.criteria.type_pagination == TypePagination.article

    def test_default_pagination_unaffected_without_legal_status_filter(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.in_code(NomCode.CDT)

        assert builder.criteria.type_pagination == TypePagination.defaut

    def test_execute_maximizes_page_size_when_status_filter_requested(self):
        """No explicit .paginate() call: the default page_size (5) is far too
        small to reach an old article's current version among many historical
        ones, so a legal-status filter must widen it to the API's max."""
        client = MagicMock()
        client.call_api.return_value = _mock_search_response([])
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.in_code(NomCode.CDT)
        builder.with_legal_status([EtatJuridique.VIGUEUR])

        builder.execute()

        sent_request = client.call_api.call_args.args[1]
        assert sent_request["recherche"]["pageSize"] == 100

    def test_execute_respects_explicit_page_size_when_status_filter_requested(self):
        """An explicit .paginate() call is a deliberate choice and must not
        be silently overridden, even though it risks missing the current
        version among many historical ones."""
        client = MagicMock()
        client.call_api.return_value = _mock_search_response([])
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.in_code(NomCode.CDT)
        builder.with_legal_status([EtatJuridique.VIGUEUR])
        builder.paginate(page_number=1, page_size=10)

        builder.execute()

        sent_request = client.call_api.call_args.args[1]
        assert sent_request["recherche"]["pageSize"] == 10

    def test_resolves_current_version_from_merged_item_and_extracts(self):
        """Reproduces the real CODE_ETAT search response shape: a single
        text-level item (global "etat", same across all its historical
        extracts) merged with a sampled list of per-version "extracts"
        (each carrying its own "legalStatus"). Only the one true current
        extract should survive the VIGUEUR filter."""
        client = MagicMock()
        client.call_api.return_value = _mock_search_response(
            [
                {
                    "etat": "VIGUEUR",
                    "moreArticlesCount": 17,
                    "sections": [
                        {
                            "id": "LEGISCTA000006199106",
                            "extracts": [
                                {
                                    "id": "LEGIARTI000037988243",
                                    "num": "787 B",
                                    "legalStatus": "MODIFIE",
                                    "type": "articles",
                                },
                                {
                                    "id": "LEGIARTI000006305436",
                                    "num": "787 B",
                                    "legalStatus": "MODIFIE",
                                    "type": "articles",
                                },
                                {
                                    "id": "LEGIARTI000053542700",
                                    "num": "787 B",
                                    "legalStatus": "VIGUEUR",
                                    "type": "articles",
                                },
                            ],
                        }
                    ],
                }
            ]
        )
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.in_code(NomCode.CDT)
        builder.with_legal_status([EtatJuridique.VIGUEUR])

        results = builder.execute()

        assert len(results) == 1
        assert results[0].id == "LEGIARTI000053542700"
        assert results[0].legal_status == "VIGUEUR"
