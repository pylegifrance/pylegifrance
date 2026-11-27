"""Unit tests for pylegifrance.models.code.search DTO conversion and
validation branches not already exercised via tests/unit/fonds/test_code_builder.py
or the integration-style code search tests.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from pylegifrance.models.code.enum import NomCode, SortCode, TypeChampCode
from pylegifrance.models.code.search import (
    ChampCode,
    CodeDateSearchRequest,
    CodeEtatSearchRequest,
    CodeSearchCriteria,
    CodeSearchResponse,
    CritereCode,
    DateVersionFiltre,
    NomCodeFiltre,
    TextLegalStatusFiltre,
)
from pylegifrance.models.constants import EtatJuridique, Operateur, TypeRecherche


def _make_critere_code(**fields: Any) -> CritereCode:
    """Build a :class:`CritereCode` from arbitrary fields.

    Routing through ``**fields: Any`` avoids a basedpyright/pydantic
    interop false positive where passing only some keyword arguments
    makes other defaulted fields (e.g. ``proximite``) look required.
    """
    return CritereCode(**fields)


def _make_date_version_filtre(**fields: Any) -> DateVersionFiltre:
    """Build a :class:`DateVersionFiltre` from arbitrary fields."""
    return DateVersionFiltre(**fields)


def _make_criteria(**fields: Any) -> CodeSearchCriteria:
    """Build a :class:`CodeSearchCriteria` from arbitrary fields.

    Also sidesteps a list-invariance false positive: a heterogeneous
    ``filtres=[NomCodeFiltre(...), DateVersionFiltre(...)]`` literal gets
    narrowly inferred by basedpyright and then rejected against the
    wider declared ``list[NomCodeFiltre | DateVersionFiltre |
    TextLegalStatusFiltre]`` parameter type.
    """
    return CodeSearchCriteria(**fields)


def _make_search_response(**fields: Any) -> CodeSearchResponse:
    """Build a :class:`CodeSearchResponse` from arbitrary fields."""
    return CodeSearchResponse(**fields)


def _criteria_with_date_filter() -> CodeSearchCriteria:
    return _make_criteria(
        champs=[
            ChampCode(
                type_champ=TypeChampCode.ALL,
                criteres=[
                    _make_critere_code(
                        type_recherche=TypeRecherche.EXACTE, valeur="L1121-1"
                    )
                ],
            )
        ],
        filtres=[
            NomCodeFiltre(valeurs=[NomCode.CC]),
            _make_date_version_filtre(single_date="2018-01-01T00:00:00"),
        ],
    )


# ---------------------------------------------------------------------------
# CritereCode.to_generated()
# ---------------------------------------------------------------------------


def test_critere_code_to_generated_includes_proximite_when_set():
    critere = _make_critere_code(
        type_recherche=TypeRecherche.EXACTE,
        valeur="propriété possession",
        proximite=5,
    )

    dto = critere.to_generated()

    assert dto.proximite == 5


def test_critere_code_to_generated_omits_proximite_when_unset():
    critere = _make_critere_code(
        type_recherche=TypeRecherche.EXACTE, valeur="propriété"
    )

    dto = critere.to_generated()

    assert dto.proximite is None


# ---------------------------------------------------------------------------
# CodeDateSearchRequest: date filter required (model_validator)
# ---------------------------------------------------------------------------


def test_code_date_search_request_requires_date_version_filtre():
    criteria_without_date = _make_criteria(
        champs=[
            ChampCode(
                type_champ=TypeChampCode.ALL,
                criteres=[
                    _make_critere_code(
                        type_recherche=TypeRecherche.EXACTE, valeur="L1121-1"
                    )
                ],
            )
        ],
        filtres=[NomCodeFiltre(valeurs=[NomCode.CC])],
    )

    with pytest.raises(ValidationError, match="CODE_DATE nécessite un filtre"):
        CodeDateSearchRequest(recherche=criteria_without_date)


def test_code_date_search_request_accepts_date_version_filtre():
    request = CodeDateSearchRequest(recherche=_criteria_with_date_filter())

    last_filtre = request.recherche.filtres[-1]
    assert isinstance(last_filtre, DateVersionFiltre)
    assert last_filtre.single_date is not None


def test_code_etat_search_request_does_not_require_date_filter():
    criteria_without_date = _make_criteria(
        champs=[
            ChampCode(
                type_champ=TypeChampCode.ALL,
                criteres=[
                    _make_critere_code(
                        type_recherche=TypeRecherche.EXACTE, valeur="L1121-1"
                    )
                ],
            )
        ],
        filtres=[
            NomCodeFiltre(valeurs=[NomCode.CC]),
            TextLegalStatusFiltre(valeurs=[EtatJuridique.VIGUEUR]),
        ],
    )

    request = CodeEtatSearchRequest(recherche=criteria_without_date)

    assert request.fond.value == "CODE_ETAT"


# ---------------------------------------------------------------------------
# CodeSearchCriteria.to_generated() DTO conversion
# ---------------------------------------------------------------------------


def test_code_search_criteria_to_generated_converts_date_fond():
    criteria = _criteria_with_date_filter()

    dto = criteria.to_generated(fond="CODE_DATE")

    assert dto.page_number == 1
    assert dto.page_size == 5
    assert dto.sort == SortCode.PERTINENCE.value
    # NomCodeFiltre converts its facette based on the fond.
    assert dto.filtres is not None
    nom_code_dto = next(f for f in dto.filtres if f.valeurs == ["Code civil"])
    assert nom_code_dto.facette == "NOM_CODE"


def test_code_search_criteria_to_generated_converts_etat_fond():
    criteria = _make_criteria(
        champs=[
            ChampCode(
                type_champ=TypeChampCode.ALL,
                criteres=[
                    _make_critere_code(
                        type_recherche=TypeRecherche.EXACTE, valeur="L1121-1"
                    )
                ],
            )
        ],
        filtres=[
            NomCodeFiltre(valeurs=[NomCode.CC]),
            TextLegalStatusFiltre(valeurs=[EtatJuridique.VIGUEUR]),
        ],
        operateur=Operateur.OU,
    )

    dto = criteria.to_generated(fond="CODE_ETAT")

    assert dto.filtres is not None
    nom_code_dto = next(f for f in dto.filtres if f.valeurs == ["Code civil"])
    assert nom_code_dto.facette == "TEXT_NOM_CODE"
    status_dto = next(f for f in dto.filtres if f.facette == "TEXT_LEGAL_STATUS")
    assert status_dto.valeurs == ["VIGUEUR"]


# ---------------------------------------------------------------------------
# CodeSearchResponse pagination properties
# ---------------------------------------------------------------------------


def test_total_pages_is_zero_when_page_size_is_zero():
    response = _make_search_response(total_results=10, page_number=1, page_size=0)

    assert response.total_pages == 0


def test_total_pages_rounds_up_for_partial_last_page():
    response = _make_search_response(total_results=11, page_number=1, page_size=5)

    assert response.total_pages == 3


def test_has_next_page_true_when_more_pages_remain():
    response = _make_search_response(total_results=11, page_number=1, page_size=5)

    assert response.has_next_page is True


def test_has_next_page_false_on_last_page():
    response = _make_search_response(total_results=11, page_number=3, page_size=5)

    assert response.has_next_page is False


def test_has_previous_page_false_on_first_page():
    response = _make_search_response(total_results=11, page_number=1, page_size=5)

    assert response.has_previous_page is False


def test_has_previous_page_true_after_first_page():
    response = _make_search_response(total_results=11, page_number=2, page_size=5)

    assert response.has_previous_page is True
