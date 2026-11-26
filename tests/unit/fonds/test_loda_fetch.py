"""Unit tests for Loda.fetch(), fetch_version_at(), fetch_versions() and the
underlying response-processing helpers (_process_consult_response,
_build_texte_model).
"""

from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.loda import HTTP_OK, Loda


def _mock_response(status_code: int, json_data) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data
    return response


def _texte_payload(**overrides) -> dict:
    """A minimal, realistic consult/lawDecree-shaped response (new format)."""
    data = {
        "id": "LEGITEXT000041952174_01-01-2021",
        "cid": "LEGITEXT000041952174",
        "title": "Loi n° 2020-734 du 17 juin 2020",
        "nor": "MTRD2011622L",
        "etat": "VIGUEUR",
        "dateDebutVersion": "2021-01-01T00:00:00",
        "dateParution": "2020-06-18T00:00:00",
        "articles": [],
        "sections": [],
    }
    data.update(overrides)
    return data


@pytest.fixture
def loda() -> Loda:
    return Loda(MagicMock())


class TestFetch:
    def test_fetch_returns_textelodat_on_success(self, loda):
        loda._client.call_api.return_value = _mock_response(HTTP_OK, _texte_payload())

        result = loda.fetch("LEGITEXT000041952174")

        assert result is not None
        assert result.titre == "Loi n° 2020-734 du 17 juin 2020"
        assert result.id == "LEGITEXT000041952174_01-01-2021"
        assert result.nor == "MTRD2011622L"
        assert result.etat == "VIGUEUR"

    def test_fetch_calls_consult_lawdecree_endpoint(self, loda):
        loda._client.call_api.return_value = _mock_response(HTTP_OK, _texte_payload())

        loda.fetch("LEGITEXT000041952174")

        args, _ = loda._client.call_api.call_args
        assert args[0] == "consult/lawDecree"
        assert args[1]["textId"] == "LEGITEXT000041952174"

    def test_fetch_extracts_date_from_text_id(self, loda):
        loda._client.call_api.return_value = _mock_response(HTTP_OK, _texte_payload())

        loda.fetch("LEGITEXT000041952174_01-01-2021")

        args, _ = loda._client.call_api.call_args
        assert args[1]["textId"] == "LEGITEXT000041952174"
        assert args[1]["date"] == "2021-01-01"

    def test_fetch_defaults_date_to_today_when_no_date_in_id(self, loda):
        loda._client.call_api.return_value = _mock_response(HTTP_OK, _texte_payload())

        loda.fetch("LEGITEXT000041952174")

        args, _ = loda._client.call_api.call_args
        # Should be a YYYY-MM-DD formatted string (today's date)
        assert len(args[1]["date"]) == 10
        assert args[1]["date"][4] == "-"

    def test_fetch_raises_on_empty_text_id(self, loda):
        with pytest.raises(ValueError):
            loda.fetch("")

    def test_fetch_returns_none_when_response_cannot_be_processed(self, loda):
        # No 'id' field at the top level -> _build_texte_model returns None
        loda._client.call_api.return_value = _mock_response(HTTP_OK, {"title": "x"})

        result = loda.fetch("LEGITEXT000041952174")

        assert result is None

    def test_fetch_old_format_with_texte_key(self, loda):
        payload = {"texte": _texte_payload()}
        loda._client.call_api.return_value = _mock_response(HTTP_OK, payload)

        result = loda.fetch("LEGITEXT000041952174")

        assert result is not None
        assert result.id == "LEGITEXT000041952174_01-01-2021"

    def test_fetch_old_format_with_invalid_texte_field(self, loda):
        payload = {"texte": None}
        loda._client.call_api.return_value = _mock_response(HTTP_OK, payload)

        result = loda.fetch("LEGITEXT000041952174")

        assert result is None

    def test_fetch_old_format_with_non_dict_texte_field(self, loda):
        payload = {"texte": "not-a-dict"}
        loda._client.call_api.return_value = _mock_response(HTTP_OK, payload)

        result = loda.fetch("LEGITEXT000041952174")

        assert result is None

    def test_fetch_returns_none_when_model_validate_raises(self, loda):
        # "id" present but data otherwise triggers a validation error in
        # TexteLodaModel.model_validate / ConsultTextResponse.model_validate.
        # A non-dict "sections" value is invalid.
        payload = _texte_payload(sections="not-a-list")
        loda._client.call_api.return_value = _mock_response(HTTP_OK, payload)

        result = loda.fetch("LEGITEXT000041952174")

        assert result is None


class TestFetchVersionAt:
    def test_fetch_version_at_success(self, loda):
        loda._client.call_api.return_value = _mock_response(HTTP_OK, _texte_payload())

        result = loda.fetch_version_at("LEGITEXT000041952174", "2021-01-01")

        assert result is not None
        assert result.titre == "Loi n° 2020-734 du 17 juin 2020"

        args, _ = loda._client.call_api.call_args
        assert args[0] == "consult/loda/version"
        assert args[1] == {
            "textId": "LEGITEXT000041952174",
            "year": 2021,
            "month": 1,
            "dayOfMonth": 1,
        }

    def test_fetch_version_at_raises_on_empty_text_id(self, loda):
        with pytest.raises(ValueError):
            loda.fetch_version_at("", "2021-01-01")

    def test_fetch_version_at_raises_on_invalid_date(self, loda):
        with pytest.raises(ValueError):
            loda.fetch_version_at("LEGITEXT000041952174", "not-a-date")

    def test_fetch_version_at_returns_none_on_non_200(self, loda):
        loda._client.call_api.return_value = _mock_response(404, {})

        result = loda.fetch_version_at("LEGITEXT000041952174", "2021-01-01")

        assert result is None

    def test_fetch_version_at_returns_none_when_unprocessable(self, loda):
        loda._client.call_api.return_value = _mock_response(HTTP_OK, {"title": "x"})

        result = loda.fetch_version_at("LEGITEXT000041952174", "2021-01-01")

        assert result is None


class TestFetchVersions:
    def test_fetch_versions_success(self, loda):
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK,
            [_texte_payload(id="v1"), _texte_payload(id="v2")],
        )

        results = loda.fetch_versions("LEGITEXT000041952174")

        assert len(results) == 2
        assert results[0].id == "v1"
        assert results[1].id == "v2"

        args, _ = loda._client.call_api.call_args
        assert args[0] == "consult/loda/versions"
        assert args[1] == {"textId": "LEGITEXT000041952174"}

    def test_fetch_versions_raises_on_empty_text_id(self, loda):
        with pytest.raises(ValueError):
            loda.fetch_versions("")

    def test_fetch_versions_returns_empty_list_on_non_200(self, loda):
        loda._client.call_api.return_value = _mock_response(404, [])

        assert loda.fetch_versions("LEGITEXT000041952174") == []

    def test_fetch_versions_returns_empty_list_when_not_a_list(self, loda):
        loda._client.call_api.return_value = _mock_response(HTTP_OK, {"not": "a list"})

        assert loda.fetch_versions("LEGITEXT000041952174") == []

    def test_fetch_versions_skips_unprocessable_entries(self, loda):
        loda._client.call_api.return_value = _mock_response(
            HTTP_OK,
            [_texte_payload(id="v1"), {"title": "no id field"}],
        )

        results = loda.fetch_versions("LEGITEXT000041952174")

        assert len(results) == 1
        assert results[0].id == "v1"
