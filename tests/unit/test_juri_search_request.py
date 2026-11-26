"""Unit tests for :class:`pylegifrance.models.juri.search.SearchRequest`.

These are pure model/construction tests: field defaults, validators, and
``to_api_model()`` conversion to the generated ``SearchRequestDTO``. No
network or client mocking is involved.
"""

from typing import Any

import pytest

from pylegifrance.models.generated.model import TypeChamp, TypePagination, TypeRecherche
from pylegifrance.models.juri.constants import PublicationStatus, SortOptions
from pylegifrance.models.juri.search import SearchRequest, SearchResponse


def _make_search_request(**fields: Any) -> SearchRequest:
    """Construct a :class:`SearchRequest` via ``**kwargs`` splat.

    Routing through this helper avoids a basedpyright/pydantic interop
    limitation where passing some-but-not-all keyword arguments directly
    to a generated model's constructor makes every other field look
    required, even though they all have defaults.
    """
    return SearchRequest(**fields)


class TestSearchRequestDefaults:
    def test_default_values(self):
        req = _make_search_request()
        assert req.search == ""
        assert req.publication_bulletin is None
        assert req.sort == SortOptions.RELEVANCE
        assert req.field == TypeChamp.all
        assert req.search_type == TypeRecherche.un_des_mots
        assert req.page_size == 5
        assert req.page_number == 1
        assert req.formatter is True
        assert req.fetch_all is False
        assert req.keys is None
        assert req.juridiction_judiciaire is None
        assert req.date_start is None
        assert req.date_end is None
        assert req.date_facet == "DATE_DECISION"
        assert req.formation is None
        assert req.cour_appel is None

    def test_construct_with_search_text(self):
        req = _make_search_request(search="licenciement")
        assert req.search == "licenciement"

    def test_page_size_bounds(self):
        with pytest.raises(ValueError):
            _make_search_request(page_size=0)
        with pytest.raises(ValueError):
            _make_search_request(page_size=101)
        assert _make_search_request(page_size=1).page_size == 1
        assert _make_search_request(page_size=100).page_size == 100

    def test_page_number_lower_bound(self):
        with pytest.raises(ValueError):
            _make_search_request(page_number=0)


class TestSearchRequestDateValidation:
    def test_valid_iso_dates_accepted(self):
        req = _make_search_request(date_start="2020-01-01", date_end="2020-12-31")
        assert req.date_start == "2020-01-01"
        assert req.date_end == "2020-12-31"

    def test_invalid_date_start_format_raises(self):
        with pytest.raises(ValueError, match="ISO format"):
            _make_search_request(date_start="01/01/2020")

    def test_invalid_date_end_format_raises(self):
        with pytest.raises(ValueError, match="ISO format"):
            _make_search_request(date_end="not-a-date")

    def test_end_before_start_raises(self):
        with pytest.raises(ValueError, match="End date must be after start date"):
            _make_search_request(date_start="2020-12-31", date_end="2020-01-01")

    def test_end_equal_to_start_is_allowed(self):
        req = _make_search_request(date_start="2020-01-01", date_end="2020-01-01")
        assert req.date_end == "2020-01-01"

    def test_date_end_alone_is_allowed(self):
        req = _make_search_request(date_end="2020-01-01")
        assert req.date_end == "2020-01-01"


class TestSearchRequestToApiModel:
    def test_basic_criteria_and_field(self):
        req = _make_search_request(search="licenciement")
        dto = req.to_api_model()

        assert dto.fond.value == "JURI"
        champ = dto.recherche.champs[0]
        assert champ.criteres is not None
        assert champ.criteres[0].valeur == "licenciement"
        assert champ.type_champ == TypeChamp.all
        assert dto.recherche.filtres == []

    def test_pagination_and_sort_forwarded(self):
        req = _make_search_request(
            search="licenciement",
            page_number=3,
            page_size=20,
            sort=SortOptions.DATE_DESC,
        )
        dto = req.to_api_model()

        assert dto.recherche.page_number == 3
        assert dto.recherche.page_size == 20
        assert dto.recherche.sort == "DATE_DESC"
        assert dto.recherche.second_sort == "ID"
        assert dto.recherche.type_pagination == TypePagination.defaut
        assert dto.recherche.from_advanced_recherche is False

    def test_publication_bulletin_filter(self):
        req = _make_search_request(
            search="licenciement",
            publication_bulletin=[PublicationStatus.PUBLISHED],
        )
        dto = req.to_api_model()

        filtres = dto.recherche.filtres
        assert filtres is not None
        assert len(filtres) == 1
        assert filtres[0].facette == "CASSATION_TYPE_PUBLICATION_BULLETIN"
        assert filtres[0].valeurs == ["T"]

    def test_jurisdiction_filter(self):
        req = _make_search_request(
            search="licenciement",
            juridiction_judiciaire=["Cour de cassation"],
        )
        dto = req.to_api_model()

        filtres = dto.recherche.filtres
        assert filtres is not None
        assert len(filtres) == 1
        assert filtres[0].facette == "JURIDICTION_JUDICIAIRE"
        assert filtres[0].valeurs == ["Cour de cassation"]

    def test_date_filter_requires_both_bounds(self):
        req = _make_search_request(search="licenciement", date_start="2020-01-01")
        dto = req.to_api_model()
        assert dto.recherche.filtres == []

        req2 = _make_search_request(
            search="licenciement", date_start="2020-01-01", date_end="2020-12-31"
        )
        dto2 = req2.to_api_model()
        filtres = dto2.recherche.filtres
        assert filtres is not None
        assert len(filtres) == 1
        entry = filtres[0]
        assert entry.facette == "DATE_DECISION"
        dates = entry.dates
        assert dates is not None
        assert dates.start is not None
        assert dates.end is not None
        assert dates.start.isoformat().startswith("2020-01-01")
        assert dates.end.isoformat().startswith("2020-12-31")

    def test_date_filter_uses_custom_date_facet(self):
        req = _make_search_request(
            search="licenciement",
            date_start="2020-01-01",
            date_end="2020-12-31",
            date_facet="DATE_PUBLI",
        )
        dto = req.to_api_model()
        filtres = dto.recherche.filtres
        assert filtres is not None
        assert filtres[0].facette == "DATE_PUBLI"

    def test_formation_filter(self):
        req = _make_search_request(search="licenciement", formation=["Chambre sociale"])
        dto = req.to_api_model()

        filtres = dto.recherche.filtres
        assert filtres is not None
        assert len(filtres) == 1
        assert filtres[0].facette == "CASSATION_FORMATION"
        assert filtres[0].valeurs == ["Chambre sociale"]

    def test_cour_appel_filter_requires_juridictions_appel(self):
        # cour_appel alone (without juridiction_judiciaire containing
        # "Juridictions d'appel") must NOT produce a filter.
        req = _make_search_request(search="licenciement", cour_appel=["PARIS"])
        dto = req.to_api_model()
        assert dto.recherche.filtres == []

    def test_cour_appel_filter_applied_with_juridictions_appel(self):
        req = _make_search_request(
            search="licenciement",
            cour_appel=["PARIS"],
            juridiction_judiciaire=["Juridictions d'appel"],
        )
        dto = req.to_api_model()

        filtres = dto.recherche.filtres
        assert filtres is not None
        facettes = {f.facette for f in filtres}
        assert "APPEL_SIEGE_APPEL" in facettes
        assert "JURIDICTION_JUDICIAIRE" in facettes

        cour_appel_filter = next(f for f in filtres if f.facette == "APPEL_SIEGE_APPEL")
        assert cour_appel_filter.valeurs == ["PARIS"]

    def test_multiple_filters_combine(self):
        req = _make_search_request(
            search="licenciement",
            publication_bulletin=[PublicationStatus.PUBLISHED],
            juridiction_judiciaire=["Cour de cassation"],
            date_start="2020-01-01",
            date_end="2020-12-31",
            formation=["Chambre sociale"],
        )
        dto = req.to_api_model()

        filtres = dto.recherche.filtres
        assert filtres is not None
        facettes = {f.facette for f in filtres}
        assert facettes == {
            "CASSATION_TYPE_PUBLICATION_BULLETIN",
            "JURIDICTION_JUDICIAIRE",
            "DATE_DECISION",
            "CASSATION_FORMATION",
        }

    def test_search_type_forwarded_to_criteria(self):
        req = _make_search_request(
            search="licenciement", search_type=TypeRecherche.exacte
        )
        dto = req.to_api_model()
        criteres = dto.recherche.champs[0].criteres
        assert criteres is not None
        assert criteres[0].type_recherche == TypeRecherche.exacte

    def test_field_forwarded_to_champ(self):
        req = _make_search_request(search="licenciement", field=TypeChamp.title)
        dto = req.to_api_model()
        assert dto.recherche.champs[0].type_champ == TypeChamp.title

    def test_proximity_forwarded_to_criteria(self):
        """Légifrance's "proximité N mots" search option."""
        req = _make_search_request(search="dommages intérêts", proximity=3)
        dto = req.to_api_model()
        criteres = dto.recherche.champs[0].criteres
        assert criteres is not None
        assert criteres[0].proximite == 3

    def test_proximity_defaults_to_none(self):
        req = _make_search_request(search="licenciement")
        dto = req.to_api_model()
        criteres = dto.recherche.champs[0].criteres
        assert criteres is not None
        assert criteres[0].proximite is None


class TestSearchResponse:
    def test_parses_aliased_fields(self):
        resp = SearchResponse(
            totalNbResult=3,
            executionTime=42,
            results=[{"id": "1"}],
            pageNumber=1,
            pageSize=10,
        )
        assert resp.total_results == 3
        assert resp.execution_time == 42
        assert resp.results == [{"id": "1"}]
        assert resp.page_number == 1
        assert resp.page_size == 10

    def test_results_defaults_to_empty_list(self):
        resp = SearchResponse(
            totalNbResult=0, executionTime=1, pageNumber=1, pageSize=10
        )
        assert resp.results == []
