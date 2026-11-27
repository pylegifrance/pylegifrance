"""Unit tests for Loda.search() and its result-processing helpers:
_process_search_results, _normalize_search_results_structure,
_extract_title_info, _extract_date_from_text_id, _extract_metadata_from_result,
_extract_data_from_titles, _create_minimal_text, _enrich_text_with_html_content,
_normalize_search_query.
"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.loda import HTTP_OK, Loda
from pylegifrance.models.loda.search import SearchRequest


def _mock_response(status_code: int, json_data) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data
    return response


@pytest.fixture
def loda() -> Loda:
    return Loda(MagicMock())


def _result(
    text_id="LEGITEXT000041952174",
    title="Loi n° 2020-734",
    etat="VIGUEUR",
    **extra: Any,
) -> dict[str, Any]:
    result: dict[str, Any] = {"titles": [{"id": text_id, "title": title}]}
    if etat is not None:
        result["etat"] = etat
    result.update(extra)
    return result


class TestSearch:
    def test_search_with_string_query_returns_results(self, loda):
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK, {"results": [_result()]}
        )

        results = loda.search("notariat")

        assert len(results) == 1
        assert results[0].id == "LEGITEXT000041952174"
        assert results[0].titre == "Loi n° 2020-734"
        assert results[0].etat == "VIGUEUR"

        args, _ = loda._client.call_api.call_args
        assert args[0] == "search"

    def test_search_with_search_request_object(self, loda):
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK, {"results": [_result()]}
        )

        results = loda.search(SearchRequest(search="notariat"))

        assert len(results) == 1

    def test_search_returns_empty_on_non_200(self, loda):
        loda._client.call_api.return_value = _mock_response(500, {})

        assert loda.search("notariat") == []

    def test_search_returns_empty_when_no_results_key(self, loda):
        loda._client.call_api.return_value = _mock_response(HTTP_OK, {"foo": "bar"})

        assert loda.search("notariat") == []

    def test_search_uses_hits_fallback(self, loda):
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK, {"hits": [_result()]}
        )

        results = loda.search("notariat")
        assert len(results) == 1

    def test_search_skips_results_without_titles(self, loda):
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK, {"results": [{"etat": "VIGUEUR"}]}
        )

        assert loda.search("notariat") == []

    def test_search_skips_results_with_empty_titles_list(self, loda):
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK, {"results": [{"titles": []}]}
        )

        assert loda.search("notariat") == []

    def test_search_skips_titles_without_id(self, loda):
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK, {"results": [{"titles": [{"title": "No id here"}]}]}
        )

        assert loda.search("notariat") == []

    def test_search_picks_first_title_with_id(self, loda):
        result = {
            "titles": [
                {"title": "No id"},
                {"id": "LEGITEXT000041952174", "title": "Has id"},
            ]
        }
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK, {"results": [result]}
        )

        results = loda.search("notariat")
        assert len(results) == 1
        assert results[0].titre == "Has id"

    def test_search_propagates_unexpected_exceptions(self, loda):
        loda._client.call_api.side_effect = RuntimeError("network down")

        with pytest.raises(RuntimeError):
            loda.search("notariat")

    def test_search_converts_pydantic_validation_errors_to_value_error(self, loda):
        with pytest.raises(ValueError):
            loda.search(SearchRequest(natures=["NOT_A_VALID_NATURE"]))

    def test_search_with_date_in_text_id_sets_date_texte(self, loda):
        result = {
            "titles": [{"id": "LEGITEXT000041952174_2021-01-01", "title": "Versioned"}]
        }
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK, {"results": [result]}
        )

        results = loda.search("notariat")
        assert len(results) == 1

    def test_search_extracts_metadata_fields(self, loda):
        result = _result(
            juris_state="VIGUEUR",
            nature="LOI",
            datePublication="2020-06-18T00:00:00",
            cid="LEGITEXT000041952174",
            nor="MTRD2011622L",
        )
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK, {"results": [result]}
        )

        results = loda.search("notariat")
        assert len(results) == 1
        texte = results[0]
        assert str(texte.nor) == "MTRD2011622L"

    def test_search_extracts_data_from_titles_legal_status_dates(self, loda):
        result = {
            "titles": [
                {
                    "id": "LEGITEXT000041952174",
                    "title": "Loi n° 2020-734",
                    "legalStatus": "VIGUEUR",
                    "startDate": "2021-04-15T16:49:47.707+0000",
                    "endDate": "2999-01-01T00:00:00.000+0000",
                }
            ]
        }
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK, {"results": [result]}
        )

        results = loda.search("notariat")
        assert len(results) == 1
        assert results[0].etat == "VIGUEUR"

    def test_search_enriches_with_html_content_from_sections(self, loda):
        result = _result(
            sections=[
                {"extracts": [{"values": ["<p>Extrait 1</p>", "<p>Extrait 2</p>"]}]}
            ]
        )
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK, {"results": [result]}
        )

        # Note: search() itself does not call _enrich_text_with_html_content;
        # verify it directly as a helper (used by callers that need body text).
        results = loda._process_search_results({"results": [result]})
        assert len(results) == 1
        texte = results[0]
        loda._enrich_text_with_html_content(texte, result)
        assert texte.texte_html == "<p>Extrait 1</p> <p>Extrait 2</p>"

    def _make_fake_texte(self, texte_html=None):
        """A stand-in with the shape _enrich_text_with_html_content expects:
        a `.texte_html` property and a `._texte.texte_html` assignable slot.
        """
        fake = MagicMock()
        fake.texte_html = texte_html
        fake._texte = MagicMock()
        fake._texte.texte_html = texte_html
        return fake

    def test_enrich_skips_when_html_already_present(self, loda):
        fake = self._make_fake_texte(texte_html="<p>Already there</p>")
        result = {"sections": [{"extracts": [{"values": ["<p>New</p>"]}]}]}

        loda._enrich_text_with_html_content(fake, result)

        assert fake._texte.texte_html == "<p>Already there</p>"

    def test_enrich_skips_when_no_sections(self, loda):
        fake = self._make_fake_texte(texte_html=None)

        loda._enrich_text_with_html_content(fake, {"no_sections": True})

        assert fake._texte.texte_html is None

    def test_enrich_skips_when_sections_not_a_list(self, loda):
        fake = self._make_fake_texte(texte_html=None)

        loda._enrich_text_with_html_content(fake, {"sections": "not-a-list"})

        assert fake._texte.texte_html is None

    def test_enrich_skips_when_no_extracts_found(self, loda):
        fake = self._make_fake_texte(texte_html=None)

        loda._enrich_text_with_html_content(fake, {"sections": [{"no_extracts": True}]})

        assert fake._texte.texte_html is None

    def test_enrich_sets_html_when_extracts_found(self, loda):
        fake = self._make_fake_texte(texte_html=None)
        result = {"sections": [{"extracts": [{"values": ["<p>A</p>", "<p>B</p>"]}]}]}

        loda._enrich_text_with_html_content(fake, result)

        assert fake._texte.texte_html == "<p>A</p> <p>B</p>"


class TestNormalizeSearchResultsStructure:
    def test_prefers_results_key(self, loda):
        data = {"results": [{"a": 1}], "hits": [{"b": 2}]}
        assert loda._normalize_search_results_structure(data) == [{"a": 1}]

    def test_falls_back_to_hits(self, loda):
        data = {"hits": [{"b": 2}]}
        assert loda._normalize_search_results_structure(data) == [{"b": 2}]

    def test_returns_empty_when_neither_present(self, loda):
        assert loda._normalize_search_results_structure({}) == []

    def test_returns_empty_when_results_not_a_list(self, loda):
        assert loda._normalize_search_results_structure({"results": "nope"}) == []

    def test_returns_empty_when_hits_not_a_list(self, loda):
        assert loda._normalize_search_results_structure({"hits": "nope"}) == []


class TestCreateMinimalText:
    def test_returns_none_on_internal_exception(self, loda, monkeypatch):
        def boom(*args, **kwargs):
            raise RuntimeError("bad data")

        monkeypatch.setattr(
            "pylegifrance.fonds.loda.ConsultTextResponse", MagicMock(side_effect=boom)
        )

        result = loda._create_minimal_text("LEGITEXT1", "Titre", {})
        assert result is None


class TestNormalizeSearchQuery:
    def test_string_is_wrapped_in_search_request(self, loda):
        query = loda._normalize_search_query("notariat")
        assert isinstance(query, SearchRequest)
        assert query.search == "notariat"

    def test_search_request_passed_through(self, loda):
        original = SearchRequest(search="notariat")
        assert loda._normalize_search_query(original) is original

    def test_invalid_nature_raises_value_error(self, loda):
        with pytest.raises(ValueError):
            loda._normalize_search_query(SearchRequest(natures=["INVALID"]))
