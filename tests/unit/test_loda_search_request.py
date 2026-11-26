"""Unit tests for :class:`pylegifrance.models.loda.search.SearchRequest`.

Pure model/construction tests: field defaults, the custom ``natures``
validation in ``__init__``, and ``to_generated_model()`` conversion to the
generated ``SearchRequestDTO`` dict. No network or client mocking involved.
"""

from datetime import datetime

import pytest

from pylegifrance.models.generated.model import (
    DatePeriod,
    Fond,
    TypeChamp,
    TypePagination,
    TypeRecherche,
)
from pylegifrance.models.generated.model import Nature2 as Nature
from pylegifrance.models.loda.search import SearchRequest


class TestSearchRequestDefaults:
    def test_default_values(self):
        req = SearchRequest()
        assert req.search is None
        assert req.text_id is None
        assert req.champ == TypeChamp.all
        assert req.type_recherche == TypeRecherche.tous_les_mots_dans_un_champ
        assert req.fond == Fond.loda_date
        assert req.natures == []
        assert req.date_signature is None
        assert req.date_publication is None
        assert req.page_number == 1
        assert req.page_size == 10

    def test_construct_with_search_text(self):
        req = SearchRequest(search="licenciement")
        assert req.search == "licenciement"


class TestNaturesValidation:
    def test_accepts_nature_enum_members(self):
        req = SearchRequest(natures=[Nature.loi, Nature.decret])
        assert req.natures == [Nature.loi, Nature.decret]

    def test_accepts_valid_string_values(self):
        req = SearchRequest(natures=["LOI", "ORDONNANCE"])
        assert req.natures == ["LOI", "ORDONNANCE"]

    def test_rejects_invalid_string_value(self):
        with pytest.raises(ValueError, match="is not a valid Nature"):
            SearchRequest(natures=["NOT_A_NATURE"])

    def test_empty_natures_list_is_allowed(self):
        req = SearchRequest(natures=[])
        assert req.natures == []


class TestToGeneratedModelFields:
    def test_text_id_produces_num_field(self):
        req = SearchRequest(text_id="LEGITEXT000006070721")
        dto = req.to_generated_model()

        champs = dto["recherche"]["champs"]
        assert len(champs) == 1
        assert champs[0]["typeChamp"] == TypeChamp.num
        assert champs[0]["criteres"][0]["valeur"] == "LEGITEXT000006070721"
        assert champs[0]["criteres"][0]["typeRecherche"] == TypeRecherche.exacte

    def test_search_produces_three_fields(self):
        req = SearchRequest(search="travail")
        dto = req.to_generated_model()

        champs = dto["recherche"]["champs"]
        assert len(champs) == 3
        type_champs = {c["typeChamp"] for c in champs}
        assert type_champs == {TypeChamp.all, TypeChamp.texte, TypeChamp.title}
        all_field = next(c for c in champs if c["typeChamp"] == TypeChamp.all)
        assert (
            all_field["criteres"][0]["typeRecherche"]
            == TypeRecherche.tous_les_mots_dans_un_champ
        )
        texte_field = next(c for c in champs if c["typeChamp"] == TypeChamp.texte)
        assert texte_field["operateur"].value == "OU"
        assert texte_field["criteres"][0]["typeRecherche"] == TypeRecherche.un_des_mots
        title_field = next(c for c in champs if c["typeChamp"] == TypeChamp.title)
        assert title_field["operateur"].value == "OU"

    def test_explicit_champ_restricts_search_to_that_field(self):
        """Légifrance's "Zone de recherche" selector (e.g. search only
        article content) must be honored, not silently replaced by the
        broad ALL+TEXTE+TITLE OR-search used when champ isn't specified."""
        req = SearchRequest(search="licenciement", champ=TypeChamp.article)
        dto = req.to_generated_model()

        champs = dto["recherche"]["champs"]
        assert len(champs) == 1
        assert champs[0]["typeChamp"] == TypeChamp.article
        assert champs[0]["criteres"][0]["valeur"] == "licenciement"

    def test_explicit_type_recherche_is_honored_for_exact_phrase(self):
        """Légifrance's "Rechercher l'expression exacte" toggle (EXACTE)
        must be honored, not silently replaced by the broad OR-search."""
        req = SearchRequest(
            search="dommages et intérêts", type_recherche=TypeRecherche.exacte
        )
        dto = req.to_generated_model()

        champs = dto["recherche"]["champs"]
        assert len(champs) == 1
        assert champs[0]["criteres"][0]["typeRecherche"] == TypeRecherche.exacte
        assert champs[0]["criteres"][0]["valeur"] == "dommages et intérêts"

    def test_text_id_and_search_both_produce_four_fields(self):
        req = SearchRequest(text_id="LEGITEXT000006070721", search="travail")
        dto = req.to_generated_model()
        assert len(dto["recherche"]["champs"]) == 4

    def test_no_search_terms_produces_default_title_field(self):
        req = SearchRequest()
        dto = req.to_generated_model()

        champs = dto["recherche"]["champs"]
        assert len(champs) == 1
        assert champs[0]["typeChamp"] == TypeChamp.title
        assert champs[0]["criteres"][0]["valeur"] == " "
        assert champs[0]["criteres"][0]["typeRecherche"] == TypeRecherche.exacte

    def test_default_filters_always_present(self):
        req = SearchRequest()
        dto = req.to_generated_model()

        facettes = [f["facette"] for f in dto["recherche"]["filtres"]]
        assert "DATE_VERSION" in facettes
        assert facettes.count("TEXT_LEGAL_STATUS") == 1
        assert "ARTICLE_LEGAL_STATUS" in facettes

        date_version_filter = next(
            f for f in dto["recherche"]["filtres"] if f["facette"] == "DATE_VERSION"
        )
        assert date_version_filter["singleDate"] is not None

        legal_status_filter = next(
            f
            for f in dto["recherche"]["filtres"]
            if f["facette"] == "TEXT_LEGAL_STATUS"
        )
        assert legal_status_filter["valeurs"] == ["VIGUEUR"]

    def test_natures_filter_with_enum_members(self):
        req = SearchRequest(natures=[Nature.loi, Nature.decret])
        dto = req.to_generated_model()

        nature_filter = next(
            f for f in dto["recherche"]["filtres"] if f["facette"] == "NATURE"
        )
        assert nature_filter["valeurs"] == ["LOI", "DECRET"]

    def test_natures_filter_with_string_values(self):
        req = SearchRequest(natures=["LOI"])
        dto = req.to_generated_model()

        nature_filter = next(
            f for f in dto["recherche"]["filtres"] if f["facette"] == "NATURE"
        )
        assert nature_filter["valeurs"] == ["LOI"]

    def test_no_natures_means_no_nature_filter(self):
        req = SearchRequest()
        dto = req.to_generated_model()
        facettes = [f["facette"] for f in dto["recherche"]["filtres"]]
        assert "NATURE" not in facettes

    def test_date_signature_as_date_period(self):
        period = DatePeriod(start=datetime(2020, 1, 1), end=datetime(2020, 12, 31))
        req = SearchRequest(date_signature=period)
        dto = req.to_generated_model()

        sig_filter = next(
            f for f in dto["recherche"]["filtres"] if f["facette"] == "DATE_SIGNATURE"
        )
        assert sig_filter["dates"]["start"] == datetime(2020, 1, 1)
        assert sig_filter["dates"]["end"] == datetime(2020, 12, 31)

    def test_date_signature_as_iso_string(self):
        req = SearchRequest(date_signature="2020-06-15")
        dto = req.to_generated_model()

        sig_filter = next(
            f for f in dto["recherche"]["filtres"] if f["facette"] == "DATE_SIGNATURE"
        )
        # Both start and end are set to the same parsed date.
        assert sig_filter["dates"]["start"] == datetime(2020, 6, 15)
        assert sig_filter["dates"]["end"] == datetime(2020, 6, 15)

    def test_no_date_signature_means_no_filter(self):
        req = SearchRequest()
        dto = req.to_generated_model()
        facettes = [f["facette"] for f in dto["recherche"]["filtres"]]
        assert "DATE_SIGNATURE" not in facettes

    def test_date_publication_as_date_period(self):
        period = DatePeriod(start=datetime(2019, 1, 1), end=datetime(2019, 6, 30))
        req = SearchRequest(date_publication=period)
        dto = req.to_generated_model()

        pub_filter = next(
            f for f in dto["recherche"]["filtres"] if f["facette"] == "DATE_PUBLICATION"
        )
        assert pub_filter["dates"]["start"] == datetime(2019, 1, 1)
        assert pub_filter["dates"]["end"] == datetime(2019, 6, 30)

    def test_date_publication_as_iso_string(self):
        req = SearchRequest(date_publication="2019-03-01")
        dto = req.to_generated_model()

        pub_filter = next(
            f for f in dto["recherche"]["filtres"] if f["facette"] == "DATE_PUBLICATION"
        )
        assert pub_filter["dates"]["start"] == datetime(2019, 3, 1)

    def test_no_date_publication_means_no_filter(self):
        req = SearchRequest()
        dto = req.to_generated_model()
        facettes = [f["facette"] for f in dto["recherche"]["filtres"]]
        assert "DATE_PUBLICATION" not in facettes

    def test_loda_etat_does_not_duplicate_legal_status_filter(self):
        req = SearchRequest(fond=Fond.loda_etat)
        dto = req.to_generated_model()
        facettes = [f["facette"] for f in dto["recherche"]["filtres"]]
        assert facettes.count("TEXT_LEGAL_STATUS") == 1

    def test_pagination_and_sort_forwarded(self):
        req = SearchRequest(page_number=3, page_size=25)
        dto = req.to_generated_model()
        assert dto["recherche"]["pageNumber"] == 3
        assert dto["recherche"]["pageSize"] == 25
        assert dto["recherche"]["sort"] == "PUBLICATION_DATE_DESC"
        assert dto["recherche"]["typePagination"] == TypePagination.defaut

    def test_fond_forwarded_to_top_level(self):
        req = SearchRequest(fond=Fond.loda_etat)
        dto = req.to_generated_model()
        assert dto["fond"] == Fond.loda_etat
