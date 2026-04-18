"""Unit tests for CodeSearchBuilder normalization and post-filtering."""

import json
from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.code import CodeSearchBuilder, _normalize_article_number
from pylegifrance.models.code.enum import NomCode
from pylegifrance.models.constants import EtatJuridique

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
