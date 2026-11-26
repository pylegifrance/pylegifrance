"""Unit tests for CodeSearchBuilder.execute() error paths, CodeConsultFetcher,
ArticleFetcher, and the high-level Code facade in pylegifrance.fonds.code.

All tests mock only LegifranceClient (via MagicMock) and exercise the real
classes under test, matching actual current behaviour of the API responses
(camelCase JSON shapes), not aspirational behaviour.
"""

import json
from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.code import (
    ArticleFetcher,
    Code,
    CodeConsultFetcher,
    CodeSearchBuilder,
    _extract_articles_from_response,
)
from pylegifrance.models.code.enum import NomCode
from pylegifrance.models.code.search import NomCodeFiltre
from pylegifrance.models.constants import EtatJuridique

# ---------------------------------------------------------------------------
# CodeSearchBuilder.execute() error / validation paths
# ---------------------------------------------------------------------------


class TestExecuteValidation:
    def test_execute_raises_when_no_filtres_and_no_champs(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")

        with pytest.raises(ValueError, match="filtre ou un champ"):
            builder.execute()

        client.call_api.assert_not_called()

    def test_execute_code_date_without_date_filter_raises(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_DATE")
        # A text search without a date filter and without a NomCodeFiltre
        # is not a "complete code search", so CODE_DATE requires at_date().
        builder.text("propriété")

        with pytest.raises(ValueError, match="CODE_DATE nécessite un filtre de date"):
            builder.execute()

        client.call_api.assert_not_called()

    def test_execute_code_date_complete_code_search_adds_today(self):
        """A bare in_code() search on CODE_DATE (no champs, NomCodeFiltre only)
        is treated as a 'complete code search' and auto-adds today's date
        instead of raising."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {"pageNumber": 1, "pageSize": 10, "totalResults": 0, "results": []}
        )
        client.call_api.return_value = mock_response

        builder = CodeSearchBuilder(client, "CODE_DATE")
        builder.in_code(NomCode.CC)
        results = builder.execute()

        assert results == []
        client.call_api.assert_called_once()
        # A DateVersionFiltre should have been appended automatically.
        from pylegifrance.models.code.search import DateVersionFiltre

        assert any(isinstance(f, DateVersionFiltre) for f in builder._filtres)

    def test_execute_unsupported_fond_raises(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "NOT_A_FOND")
        builder.text("foo")

        with pytest.raises(ValueError, match="Type de fond non supporté"):
            builder.execute()

    def test_execute_with_date_filter_on_code_date_succeeds(self):
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {"pageNumber": 1, "pageSize": 10, "totalResults": 0, "results": []}
        )
        client.call_api.return_value = mock_response

        builder = CodeSearchBuilder(client, "CODE_DATE")
        builder.text("propriété").at_date("2020-01-01")
        results = builder.execute()

        assert results == []
        client.call_api.assert_called_once()

    def test_execute_returns_empty_list_when_response_falsy(self):
        client = MagicMock()
        client.call_api.return_value = None

        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.text("propriété")
        results = builder.execute()

        assert results == []

    def test_execute_respects_page_size_limit(self):
        """execute() stops appending results once page_size is reached."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(
            {
                "pageNumber": 1,
                "pageSize": 1,
                "totalResults": 2,
                "results": [
                    {"id": "LEGIARTI000001", "num": "1"},
                    {"id": "LEGIARTI000002", "num": "2"},
                ],
            }
        )
        client.call_api.return_value = mock_response

        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.text("propriété").paginate(page_number=1, page_size=1)
        results = builder.execute()

        assert len(results) == 1
        assert results[0].id == "LEGIARTI000001"


class TestPaginateValidation:
    def test_paginate_rejects_page_number_below_one(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        with pytest.raises(ValueError, match="numéro de page"):
            builder.paginate(page_number=0)

    def test_paginate_rejects_page_size_below_one(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        with pytest.raises(ValueError, match="taille de page"):
            builder.paginate(page_size=0)

    def test_paginate_rejects_page_size_above_100(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        with pytest.raises(ValueError, match="taille de page"):
            builder.paginate(page_size=101)

    def test_paginate_sets_criteria(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.paginate(page_number=2, page_size=25)
        assert builder.criteria.page_number == 2
        assert builder.criteria.page_size == 25


class TestAtDateValidation:
    def test_at_date_rejects_non_code_date_fond(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        with pytest.raises(ValueError, match="CODE_DATE"):
            builder.at_date("2020-01-01")

    def test_at_date_rejects_invalid_format(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_DATE")
        with pytest.raises(ValueError, match="Format de date invalide"):
            builder.at_date("not-a-date")


class TestWithLegalStatusValidation:
    def test_with_legal_status_rejects_non_code_etat_fond(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_DATE")
        with pytest.raises(ValueError, match="CODE_ETAT"):
            builder.with_legal_status()

    def test_with_legal_status_defaults_to_vigueur(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.with_legal_status()
        assert builder._requested_statuses == [EtatJuridique.VIGUEUR]


class TestInCodes:
    def test_in_codes_accepts_enum_members(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.in_codes([NomCode.CC, NomCode.CP])
        last_filtre = builder._filtres[-1]
        assert isinstance(last_filtre, NomCodeFiltre)
        assert last_filtre.valeurs == [NomCode.CC, NomCode.CP]

    def test_in_codes_accepts_valid_enum_name_string(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.in_codes(["CC"])
        last_filtre = builder._filtres[-1]
        assert isinstance(last_filtre, NomCodeFiltre)
        assert last_filtre.valeurs == [NomCode.CC]

    def test_in_codes_accepts_valid_enum_value_string(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        builder.in_codes(["Code civil"])
        last_filtre = builder._filtres[-1]
        assert isinstance(last_filtre, NomCodeFiltre)
        assert last_filtre.valeurs == ["Code civil"]

    def test_in_codes_rejects_invalid_string(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        with pytest.raises(ValueError, match="Nom de code invalide"):
            builder.in_codes(["NOT_A_REAL_CODE"])


class TestWithFormatter:
    def test_with_formatter_sets_flag(self):
        client = MagicMock()
        builder = CodeSearchBuilder(client, "CODE_ETAT")
        assert builder._formatter is False
        builder.with_formatter()
        assert builder._formatter is True


# ---------------------------------------------------------------------------
# _extract_articles_from_response
# ---------------------------------------------------------------------------


class TestExtractArticlesFromResponse:
    def test_yields_flat_item_without_sections(self):
        results = [{"id": "LEGIARTI000001", "num": "1"}]
        extracted = list(_extract_articles_from_response(results, formatter=False))
        assert extracted == [{"id": "LEGIARTI000001", "num": "1"}]

    def test_merges_section_extracts_of_type_articles(self):
        results = [
            {
                "id": "top",
                "sections": [
                    {
                        "id": "SECTION1",
                        "extracts": [
                            {"type": "articles", "num": "1", "id": "LEGIARTI1"},
                            {"type": "sommaire", "num": "2"},
                        ],
                    }
                ],
            }
        ]
        extracted = list(_extract_articles_from_response(results, formatter=False))
        assert len(extracted) == 1
        assert extracted[0]["num"] == "1"
        assert extracted[0]["id"] == "LEGIARTI1"
        # formatter disabled: no cid injected from section
        assert "cid" not in extracted[0]

    def test_formatter_injects_section_cid(self):
        results = [
            {
                "id": "top",
                "sections": [
                    {
                        "id": "SECTION1",
                        "extracts": [
                            {"type": "articles", "num": "1", "id": "LEGIARTI1"},
                        ],
                    }
                ],
            }
        ]
        extracted = list(_extract_articles_from_response(results, formatter=True))
        assert extracted[0]["cid"] == "SECTION1"

    def test_empty_sections_list_yields_nothing_from_that_item(self):
        results = [{"id": "top", "sections": []}]
        extracted = list(_extract_articles_from_response(results, formatter=False))
        # "sections" in item is True but item["sections"] is empty/falsy,
        # so the else branch (yield item) fires.
        assert extracted == [{"id": "top", "sections": []}]

    def test_section_without_extracts_key_yields_nothing(self):
        results = [{"id": "top", "sections": [{"id": "SECTION1"}]}]
        extracted = list(_extract_articles_from_response(results, formatter=False))
        assert extracted == []


# ---------------------------------------------------------------------------
# CodeConsultFetcher
# ---------------------------------------------------------------------------


def _mock_consult_response(payload: dict) -> MagicMock:
    mock = MagicMock()
    mock.json.return_value = payload
    return mock


class TestCodeConsultFetcherAt:
    def test_at_with_iso_date_executes_and_returns_code(self):
        client = MagicMock()
        client.call_api.return_value = _mock_consult_response(
            {
                "id": "LEGITEXT000006070721",
                "cid": "LEGITEXT000006070721",
                "title": "Code civil",
                "etat": "VIGUEUR",
                "sections": None,
                "articles": None,
            }
        )
        fetcher = CodeConsultFetcher(client, "LEGITEXT000006070721")
        code = fetcher.at("2020-01-01")

        assert code.title == "Code civil"
        assert fetcher.date == "2020-01-01"
        client.call_api.assert_called_once()
        endpoint, payload = client.call_api.call_args[0]
        assert endpoint == "consult/code"
        assert payload["date"] == "2020-01-01"

    def test_at_with_timestamp_converts_to_iso_date(self):
        client = MagicMock()
        client.call_api.return_value = _mock_consult_response(
            {"id": "x", "title": "Code civil"}
        )
        fetcher = CodeConsultFetcher(client, "LEGITEXT000006070721")
        # 2020-01-01T00:00:00Z in ms
        code = fetcher.at("1577836800000")

        assert fetcher.date == "2020-01-01"
        assert code.title == "Code civil"

    def test_at_with_invalid_date_format_raises(self):
        client = MagicMock()
        fetcher = CodeConsultFetcher(client, "LEGITEXT000006070721")

        with pytest.raises(ValueError, match="Format de date invalide"):
            fetcher.at("not-a-date")

        client.call_api.assert_not_called()

    def test_at_with_short_digit_string_is_treated_as_iso_and_fails(self):
        """A short digit-only string fails the len>=10 timestamp heuristic and
        isn't a valid ISO date either, so it should raise."""
        client = MagicMock()
        fetcher = CodeConsultFetcher(client, "LEGITEXT000006070721")

        with pytest.raises(ValueError, match="Format de date invalide"):
            fetcher.at("12345")

    def test_include_abrogated_sets_flag_and_chains(self):
        client = MagicMock()
        fetcher = CodeConsultFetcher(client, "LEGITEXT000006070721")
        result = fetcher.include_abrogated()
        assert result is fetcher
        assert fetcher.abrogated is True

        fetcher.include_abrogated(False)
        assert fetcher.abrogated is False

    def test_section_sets_section_id_and_chains(self):
        client = MagicMock()
        fetcher = CodeConsultFetcher(client, "LEGITEXT000006070721")
        result = fetcher.section("LEGISCTA000006112861")
        assert result is fetcher
        assert fetcher.section_id == "LEGISCTA000006112861"

    def test_execute_uses_current_date_when_none_set(self):
        client = MagicMock()
        client.call_api.return_value = _mock_consult_response({"id": "x"})
        fetcher = CodeConsultFetcher(client, "LEGITEXT000006070721")

        fetcher._execute()

        assert fetcher.date is not None
        endpoint, payload = client.call_api.call_args[0]
        assert payload["date"] == fetcher.date

    def test_execute_passes_abrogated_and_section_through_request(self):
        client = MagicMock()
        client.call_api.return_value = _mock_consult_response({"id": "x"})
        fetcher = CodeConsultFetcher(client, "LEGITEXT000006070721")
        fetcher.include_abrogated(True).section("LEGISCTA000006112861")
        fetcher.at("2020-01-01")

        endpoint, payload = client.call_api.call_args[0]
        assert payload["abrogated"] is True
        assert payload["sctCid"] == "LEGISCTA000006112861"


# ---------------------------------------------------------------------------
# ArticleFetcher
# ---------------------------------------------------------------------------


class TestArticleFetcherAt:
    def test_at_with_iso_string_date(self):
        client = MagicMock()
        response = MagicMock()
        response.json.return_value = {
            "article": {"id": "LEGIARTI000006419292", "num": "1"}
        }
        client.call_api.return_value = response

        fetcher = ArticleFetcher(client, "LEGIARTI000006419292")
        article = fetcher.at("2020-01-01")

        assert article.id == "LEGIARTI000006419292"
        endpoint, payload = client.call_api.call_args[0]
        assert endpoint == "consult/getArticle"
        assert payload == {"id": "LEGIARTI000006419292", "date": "2020-01-01"}

    def test_at_with_datetime_object(self):
        from datetime import datetime

        client = MagicMock()
        response = MagicMock()
        response.json.return_value = {"article": {"id": "LEGIARTI1", "num": "1"}}
        client.call_api.return_value = response

        fetcher = ArticleFetcher(client, "LEGIARTI1")
        fetcher.at(datetime(2020, 1, 1))

        endpoint, payload = client.call_api.call_args[0]
        assert payload["date"] == "2020-01-01"

    def test_at_with_int_timestamp(self):
        client = MagicMock()
        response = MagicMock()
        response.json.return_value = {"article": {"id": "LEGIARTI1", "num": "1"}}
        client.call_api.return_value = response

        fetcher = ArticleFetcher(client, "LEGIARTI1")
        fetcher.at(1577836800000)

        endpoint, payload = client.call_api.call_args[0]
        assert payload["date"] == "2020-01-01"

    def test_at_with_invalid_type_raises(self):
        client = MagicMock()
        fetcher = ArticleFetcher(client, "LEGIARTI1")

        with pytest.raises(ValueError, match="Type de date invalide"):
            fetcher.at(3.14)  # type: ignore[arg-type]

    def test_at_raises_when_response_falsy(self):
        client = MagicMock()
        client.call_api.return_value = None
        fetcher = ArticleFetcher(client, "LEGIARTI1")

        with pytest.raises(ValueError, match="non trouvé"):
            fetcher.at("2020-01-01")


# ---------------------------------------------------------------------------
# Code facade
# ---------------------------------------------------------------------------


class TestCodeFacade:
    def test_search_returns_builder_bound_to_fond(self):
        client = MagicMock()
        code = Code(client, fond="CODE_DATE")
        builder = code.search()
        assert isinstance(builder, CodeSearchBuilder)
        assert builder.fond == "CODE_DATE"
        assert builder.api is client

    def test_default_fond_is_code_etat(self):
        client = MagicMock()
        code = Code(client)
        assert code.fond == "CODE_ETAT"

    def test_fetch_code_returns_consult_fetcher(self):
        client = MagicMock()
        code = Code(client)
        fetcher = code.fetch_code("LEGITEXT000006070721")
        assert isinstance(fetcher, CodeConsultFetcher)
        assert fetcher.text_id == "LEGITEXT000006070721"

    def test_fetch_article_returns_article_fetcher_for_valid_id(self):
        client = MagicMock()
        code = Code(client)
        fetcher = code.fetch_article("LEGIARTI000006419292")
        assert isinstance(fetcher, ArticleFetcher)
        assert fetcher.article_id == "LEGIARTI000006419292"

    def test_fetch_article_rejects_empty_id(self):
        client = MagicMock()
        code = Code(client)
        with pytest.raises(ValueError, match="Identifiant d'article invalide"):
            code.fetch_article("")

    def test_fetch_article_rejects_wrong_prefix(self):
        client = MagicMock()
        code = Code(client)
        with pytest.raises(ValueError, match="Identifiant d'article invalide"):
            code.fetch_article("LEGITEXT000006070721")
