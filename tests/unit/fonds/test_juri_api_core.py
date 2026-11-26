"""Unit tests for :class:`pylegifrance.fonds.juri.JuriAPI` core retrieval and
search methods not already covered by ``test_juri_verification_endpoints.py``:

- :meth:`JuriAPI.fetch`
- :meth:`JuriAPI.fetch_with_ancien_id`
- :meth:`JuriAPI.fetch_version_at`
- :meth:`JuriAPI.fetch_versions`
- :meth:`JuriAPI.search`
- :meth:`JuriAPI.fetch_by_id` (non-200 response branch)
- :meth:`JuriAPI.search_by_affaire` (date_range arity error)
- :meth:`JuriAPI._run_search_dto` edge cases (malformed results)

Mocks only ``LegifranceClient.call_api`` (via ``MagicMock``), never the class
under test, matching the style of ``test_juri_verification_endpoints.py``.
"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.juri import JuriAPI, JuriDecision
from pylegifrance.models.juri.search import SearchRequest


def _mock_response(status_code: int, payload):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


def _consult_payload(text_id: str | None = "JURITEXT000037999394") -> dict:
    if text_id is None:
        return {"text": None, "executionTime": 12}
    return {
        "text": {
            "id": text_id,
            "titre": "Arrêt du 4 mars 2020",
            "titreLong": "Cour de cassation, Chambre sociale, 4 mars 2020",
            "liens": [],
        },
        "executionTime": 12,
    }


def _search_payload(ids: list[str]) -> dict:
    return {
        "totalNbResult": len(ids),
        "executionTime": 5,
        "pageNumber": 1,
        "pageSize": 10,
        "results": [{"titles": [{"id": text_id}]} for text_id in ids],
    }


class TestFetch:
    def test_raises_on_empty_text_id(self):
        client = MagicMock()
        with pytest.raises(ValueError):
            JuriAPI(client).fetch("")
        client.call_api.assert_not_called()

    def test_returns_none_on_non_200(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(400, {})
        assert JuriAPI(client).fetch("JURITEXT000037999394") is None

    def test_returns_none_when_text_field_empty(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _consult_payload(None))
        assert JuriAPI(client).fetch("JURITEXT000000000000") is None

    def test_happy_path(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200, _consult_payload("JURITEXT000037999394")
        )
        decision = JuriAPI(client).fetch("JURITEXT000037999394")
        assert isinstance(decision, JuriDecision)
        assert decision.id == "JURITEXT000037999394"

        call_args = client.call_api.call_args
        assert call_args.args[0] == "consult/juri"
        assert call_args.args[1]["textId"] == "JURITEXT000037999394"


class TestFetchWithAncienId:
    def test_raises_on_empty_ancien_id(self):
        client = MagicMock()
        with pytest.raises(ValueError):
            JuriAPI(client).fetch_with_ancien_id("")
        client.call_api.assert_not_called()

    def test_returns_none_on_non_200(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(404, {})
        assert JuriAPI(client).fetch_with_ancien_id("JG_L_2006_09_000000269553") is None

    def test_returns_none_when_text_field_empty(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _consult_payload(None))
        assert JuriAPI(client).fetch_with_ancien_id("JG_L_2006_09_000000269553") is None

    def test_happy_path(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200, _consult_payload("JURITEXT000037999394")
        )

        decision = JuriAPI(client).fetch_with_ancien_id("JG_L_2006_09_000000269553")

        assert isinstance(decision, JuriDecision)
        assert decision.id == "JURITEXT000037999394"

        call_args = client.call_api.call_args
        assert call_args.args[0] == "consult/juri/ancienId"
        assert call_args.args[1]["ancienId"] == "JG_L_2006_09_000000269553"


class TestFetchVersionAt:
    def test_raises_on_empty_text_id(self):
        client = MagicMock()
        with pytest.raises(ValueError):
            JuriAPI(client).fetch_version_at("", "2020-03-04")
        client.call_api.assert_not_called()

    def test_raises_on_invalid_date_format(self):
        client = MagicMock()
        with pytest.raises(ValueError, match="Format de date invalide"):
            JuriAPI(client).fetch_version_at("JURITEXT000037999394", "not-a-date")
        client.call_api.assert_not_called()

    def test_returns_none_on_non_200(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(400, {})
        result = JuriAPI(client).fetch_version_at("JURITEXT000037999394", "2020-03-04")
        assert result is None

    def test_returns_none_when_text_field_empty(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _consult_payload(None))
        result = JuriAPI(client).fetch_version_at("JURITEXT000037999394", "2020-03-04")
        assert result is None

    def test_happy_path(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200, _consult_payload("JURITEXT000037999394")
        )

        result = JuriAPI(client).fetch_version_at("JURITEXT000037999394", "2020-03-04")

        assert isinstance(result, JuriDecision)
        call_args = client.call_api.call_args
        assert call_args.args[0] == "consult/juri/version"
        assert call_args.args[1] == {
            "textId": "JURITEXT000037999394",
            "date": "2020-03-04",
        }


class TestFetchVersions:
    def test_raises_on_empty_text_id(self):
        client = MagicMock()
        with pytest.raises(ValueError):
            JuriAPI(client).fetch_versions("")
        client.call_api.assert_not_called()

    def test_returns_empty_list_on_non_200(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(400, {})
        assert JuriAPI(client).fetch_versions("JURITEXT000037999394") == []

    def test_returns_empty_list_when_response_not_a_list(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, {"unexpected": "shape"})
        assert JuriAPI(client).fetch_versions("JURITEXT000037999394") == []

    def test_returns_empty_list_when_empty(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, [])
        assert JuriAPI(client).fetch_versions("JURITEXT000037999394") == []

    def test_skips_malformed_version_entries(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200,
            [
                {"text": None},
                _consult_payload("JURITEXT000037999394"),
            ],
        )

        versions = JuriAPI(client).fetch_versions("JURITEXT000037999394")

        assert len(versions) == 1
        assert versions[0].id == "JURITEXT000037999394"

    def test_happy_path_multiple_versions(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200,
            [
                _consult_payload("JURITEXT000037999394"),
                _consult_payload("JURITEXT000037999395"),
            ],
        )

        versions = JuriAPI(client).fetch_versions("JURITEXT000037999394")

        assert len(versions) == 2
        assert {v.id for v in versions} == {
            "JURITEXT000037999394",
            "JURITEXT000037999395",
        }
        call_args = client.call_api.call_args
        assert call_args.args[0] == "consult/juri/versions"
        assert call_args.args[1] == {"textId": "JURITEXT000037999394"}


class TestSearch:
    def test_accepts_plain_string_query(self):
        client = MagicMock()

        def side_effect(route, data):
            if route == "search":
                return _mock_response(200, _search_payload(["JURITEXT000037999394"]))
            if route == "consult/juri":
                return _mock_response(200, _consult_payload("JURITEXT000037999394"))
            raise AssertionError(f"unexpected route {route}")

        client.call_api.side_effect = side_effect

        results = JuriAPI(client).search("licenciement")

        assert len(results) == 1
        assert results[0].id == "JURITEXT000037999394"

        search_call = client.call_api.call_args_list[0]
        assert search_call.args[0] == "search"
        assert search_call.args[1]["fond"] == "JURI"

    def test_accepts_search_request_object(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _search_payload([]))

        results = JuriAPI(client).search(SearchRequest(search="licenciement"))

        assert results == []
        search_call = client.call_api.call_args
        assert (
            search_call.args[1]["recherche"]["champs"][0]["criteres"][0]["valeur"]
            == "licenciement"
        )

    def test_returns_empty_list_on_non_200(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(400, {})
        assert JuriAPI(client).search("licenciement") == []

    def test_returns_empty_list_when_results_missing(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, {"totalNbResult": 0})
        assert JuriAPI(client).search("licenciement") == []

    def test_returns_empty_list_when_results_not_a_list(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, {"results": "not-a-list"})
        assert JuriAPI(client).search("licenciement") == []

    def test_skips_results_without_titles(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200, {"results": [{"no_titles_key": True}]}
        )
        assert JuriAPI(client).search("licenciement") == []

    def test_skips_results_with_empty_titles_list(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200, {"results": [{"titles": []}]}
        )
        assert JuriAPI(client).search("licenciement") == []

    def test_skips_titles_without_id(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200, {"results": [{"titles": [{"no_id": True}]}]}
        )
        assert JuriAPI(client).search("licenciement") == []

    def test_skips_result_when_fetch_returns_none(self):
        client = MagicMock()

        def side_effect(route, data):
            if route == "search":
                return _mock_response(200, _search_payload(["JURITEXT000037999394"]))
            if route == "consult/juri":
                return _mock_response(200, _consult_payload(None))
            raise AssertionError(f"unexpected route {route}")

        client.call_api.side_effect = side_effect

        assert JuriAPI(client).search("licenciement") == []

    def test_skips_result_when_fetch_raises(self):
        client = MagicMock()

        def side_effect(route, data):
            if route == "search":
                return _mock_response(200, _search_payload(["JURITEXT000037999394"]))
            if route == "consult/juri":
                raise Exception("boom")
            raise AssertionError(f"unexpected route {route}")

        client.call_api.side_effect = side_effect

        assert JuriAPI(client).search("licenciement") == []


class TestFetchByIdNon200:
    def test_returns_none_on_non_200_without_exception(self):
        """A non-exception, non-200 response also maps to ``None``.

        The primary "unknown textId" path raises via ``call_api``
        (see ``test_juri_verification_endpoints.py``), but the method also
        guards a plain non-200 response defensively.
        """
        client = MagicMock()
        client.call_api.return_value = _mock_response(204, {})

        assert JuriAPI(client).fetch_by_id("JURITEXT000037999394") is None


class TestSearchByAffaireDateRangeArity:
    def test_rejects_date_range_with_wrong_arity(self):
        client = MagicMock()

        with pytest.raises(ValueError, match="tuple"):
            JuriAPI(client).search_by_affaire(
                num_affaire="18-26.218",
                date_range=(date(2020, 1, 1), date(2020, 6, 1), date(2020, 12, 1)),  # type: ignore[arg-type]
            )

        client.call_api.assert_not_called()


class TestRunSearchDtoEdgeCases:
    """Additional edge cases for the shared ``_run_search_dto`` helper,
    exercised through ``search_by_ecli`` since the helper is private."""

    def test_returns_empty_list_when_results_not_a_list(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, {"results": "not-a-list"})
        assert JuriAPI(client).search_by_ecli("ECLI:FR:CCASS:2018:CO00579") == []

    def test_skips_results_without_titles(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200, {"results": [{"no_titles": True}]}
        )
        assert JuriAPI(client).search_by_ecli("ECLI:FR:CCASS:2018:CO00579") == []

    def test_skips_titles_without_id(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200, {"results": [{"titles": [{}]}]}
        )
        assert JuriAPI(client).search_by_ecli("ECLI:FR:CCASS:2018:CO00579") == []

    def test_logs_and_skips_when_fetch_raises(self):
        client = MagicMock()

        def side_effect(route, data):
            if route == "search":
                return _mock_response(200, _search_payload(["JURITEXT000037999394"]))
            if route == "consult/juri":
                raise Exception("boom")
            raise AssertionError(f"unexpected route {route}")

        client.call_api.side_effect = side_effect

        assert JuriAPI(client).search_by_ecli("ECLI:FR:CCASS:2018:CO00579") == []
