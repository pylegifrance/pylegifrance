from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.judilibre import JudilibreAPI, JudilibreAPIError, JudilibreDecision


def test_search_wraps_results_as_decisions():
    client = MagicMock()
    client.get.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "results": [
                {
                    "id": "abc123",
                    "jurisdiction": "Cour de cassation",
                    "chamber": "Chambre sociale",
                    "decision_date": "2020-03-04",
                    "summary": "Résumé",
                    "files": [{"url": "https://judilibre.fr/abc123"}],
                }
            ]
        },
    )
    api = JudilibreAPI(client)

    results = api.search("licenciement")

    assert len(results) == 1
    assert isinstance(results[0], JudilibreDecision)
    assert results[0].id == "abc123"
    assert results[0].url == "https://judilibre.fr/abc123"


def test_search_raises_on_server_error_instead_of_returning_empty():
    client = MagicMock()
    client.get.side_effect = JudilibreAPIError(500, "internal error")
    api = JudilibreAPI(client)

    with pytest.raises(JudilibreAPIError):
        api.search("licenciement")


def test_fetch_returns_none_for_unknown_id():
    client = MagicMock()
    client.get.side_effect = JudilibreAPIError(404, "not found")
    api = JudilibreAPI(client)

    assert api.fetch("does-not-exist") is None


def test_fetch_reraises_on_server_error():
    client = MagicMock()
    client.get.side_effect = JudilibreAPIError(500, "internal error")
    api = JudilibreAPI(client)

    with pytest.raises(JudilibreAPIError):
        api.fetch("some-id")


def test_url_falls_back_to_courdecassation_when_no_files():
    decision = JudilibreDecision.__new__(JudilibreDecision)
    decision._decision = MagicMock(files=None, id="abc123")

    assert decision.url == "https://www.courdecassation.fr/decision/abc123"
