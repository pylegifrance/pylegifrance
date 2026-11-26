"""Unit tests for JudilibreAPI.search()/.fetch() edge cases not already
covered by test_judilibre_decision.py (which covers the happy-path search,
the 500/404 error paths, and the no-files url fallback).
"""

from unittest.mock import MagicMock

from pylegifrance.fonds.judilibre import JudilibreAPI, JudilibreDecision


def test_search_returns_empty_list_on_non_ok_2xx_status():
    # Defensive fallback for e.g. a 204 No Content, which client.get() would
    # not raise JudilibreAPIError for (it's not in the 400-600 range).
    client = MagicMock()
    client.get.return_value = MagicMock(status_code=204)
    api = JudilibreAPI(client)

    assert api.search("licenciement") == []


def test_search_returns_empty_list_when_no_results_key():
    client = MagicMock()
    client.get.return_value = MagicMock(status_code=200, json=lambda: {})
    api = JudilibreAPI(client)

    assert api.search("licenciement") == []


def test_search_passes_filters_as_query_params():
    client = MagicMock()
    client.get.return_value = MagicMock(status_code=200, json=lambda: {"results": []})
    api = JudilibreAPI(client)

    api.search("licenciement", jurisdiction="cc", date_start=None, page_size=10)

    client.get.assert_called_once_with(
        "search",
        params={"query": "licenciement", "jurisdiction": "cc", "page_size": 10},
    )


def test_fetch_returns_decision_on_success():
    client = MagicMock()
    client.get.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "id": "abc123",
            "jurisdiction": "Cour de cassation",
            "chamber": "Chambre sociale",
            "decision_date": "2020-03-04",
            "text": "Texte intégral.",
        },
    )
    api = JudilibreAPI(client)

    result = api.fetch("abc123")

    assert isinstance(result, JudilibreDecision)
    assert result.id == "abc123"
    assert result.text == "Texte intégral."
    client.get.assert_called_once_with("decision", params={"id": "abc123"})


def test_fetch_returns_none_on_non_ok_2xx_status():
    client = MagicMock()
    client.get.return_value = MagicMock(status_code=204)
    api = JudilibreAPI(client)

    assert api.fetch("abc123") is None
