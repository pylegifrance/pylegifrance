from unittest.mock import MagicMock

from pylegifrance.fonds.judilibre import JudilibreAPI, JudilibreDecision


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


def test_fetch_returns_none_for_unknown_id():
    client = MagicMock()
    client.get.return_value = MagicMock(status_code=404, json=lambda: {"error": "not found"})
    api = JudilibreAPI(client)

    assert api.fetch("does-not-exist") is None
