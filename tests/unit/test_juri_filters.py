"""Unit tests for :mod:`pylegifrance.models.juri.filters`.

Pure pydantic model tests: construction, default values, and field
validation for each filter class. No network or client mocking required.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from pylegifrance.models.juri.constants import (
    CoursAppel,
    FilterTypes,
    FormationsJudiciaires,
    JuridictionJudiciaire,
    PublicationStatus,
)
from pylegifrance.models.juri.filters import (
    BaseFilter,
    CourAppelFilter,
    FormationFilter,
    JurisdictionFilter,
    PublicationFilter,
)


def _make_base_filter(**fields: Any) -> BaseFilter:
    """Build a :class:`BaseFilter` from arbitrary fields.

    Routing through ``**fields: Any`` avoids a basedpyright/pydantic
    interop false positive where passing only some keyword arguments
    makes every other field look required, even when (as here) the
    omission is the point of the test.
    """
    return BaseFilter(**fields)


def _make_jurisdiction_filter(**fields: Any) -> JurisdictionFilter:
    """Build a :class:`JurisdictionFilter` from arbitrary fields."""
    return JurisdictionFilter(**fields)


def _make_formation_filter(**fields: Any) -> FormationFilter:
    """Build a :class:`FormationFilter` from arbitrary fields."""
    return FormationFilter(**fields)


def _make_cour_appel_filter(**fields: Any) -> CourAppelFilter:
    """Build a :class:`CourAppelFilter` from arbitrary fields."""
    return CourAppelFilter(**fields)


def _make_publication_filter(**fields: Any) -> PublicationFilter:
    """Build a :class:`PublicationFilter` from arbitrary fields."""
    return PublicationFilter(**fields)


class TestBaseFilter:
    def test_construct_with_facette_and_valeurs(self):
        f = BaseFilter(facette=FilterTypes.FORMATION, valeurs=["a", "b"])
        assert f.facette == FilterTypes.FORMATION
        assert list(f.valeurs) == ["a", "b"]

    def test_requires_facette(self):
        with pytest.raises(ValidationError):
            _make_base_filter(valeurs=["a"])

    def test_requires_valeurs(self):
        with pytest.raises(ValidationError):
            _make_base_filter(facette=FilterTypes.FORMATION)

    def test_accepts_empty_valeurs_sequence(self):
        f = BaseFilter(facette=FilterTypes.FORMATION, valeurs=[])
        assert list(f.valeurs) == []


class TestJurisdictionFilter:
    def test_default_facette(self):
        f = JurisdictionFilter(valeurs=[JuridictionJudiciaire.cour_de_cassation])
        assert f.facette == FilterTypes.JURIDICTION_JUDICIAIRE

    def test_accepts_valid_enum_values(self):
        f = JurisdictionFilter(
            valeurs=[
                JuridictionJudiciaire.cour_de_cassation,
                JuridictionJudiciaire.juridictions_appel,
            ]
        )
        assert list(f.valeurs) == [
            JuridictionJudiciaire.cour_de_cassation,
            JuridictionJudiciaire.juridictions_appel,
        ]

    def test_rejects_invalid_value(self):
        with pytest.raises(ValidationError):
            _make_jurisdiction_filter(valeurs=["Not a real jurisdiction"])

    def test_facette_can_be_overridden(self):
        # Pydantic allows passing the field explicitly even though it has a
        # default; this documents that the default is not enforced as a
        # constant.
        f = JurisdictionFilter(
            facette=FilterTypes.JURIDICTION_JUDICIAIRE,
            valeurs=[JuridictionJudiciaire.cour_de_cassation],
        )
        assert f.facette == FilterTypes.JURIDICTION_JUDICIAIRE


class TestFormationFilter:
    def test_default_facette(self):
        f = FormationFilter(valeurs=[FormationsJudiciaires.CHAMBRE_CIVILE_1])
        assert f.facette == FilterTypes.FORMATION

    def test_accepts_valid_enum_values(self):
        f = FormationFilter(
            valeurs=[
                FormationsJudiciaires.CHAMBRE_CIVILE_1,
                FormationsJudiciaires.CHAMBRE_CRIMINELLE,
            ]
        )
        assert list(f.valeurs) == [
            FormationsJudiciaires.CHAMBRE_CIVILE_1,
            FormationsJudiciaires.CHAMBRE_CRIMINELLE,
        ]

    def test_rejects_invalid_value(self):
        with pytest.raises(ValidationError):
            _make_formation_filter(valeurs=["NOT_A_FORMATION"])


class TestCourAppelFilter:
    def test_default_facette(self):
        f = CourAppelFilter(valeurs=[CoursAppel.PARIS])
        assert f.facette == FilterTypes.COUR_APPEL

    def test_accepts_valid_enum_values(self):
        f = CourAppelFilter(valeurs=[CoursAppel.PARIS, CoursAppel.LYON])
        assert list(f.valeurs) == [CoursAppel.PARIS, CoursAppel.LYON]

    def test_rejects_invalid_value(self):
        with pytest.raises(ValidationError):
            _make_cour_appel_filter(valeurs=["ATLANTIS"])


class TestPublicationFilter:
    def test_default_facette(self):
        f = PublicationFilter()
        assert f.facette == FilterTypes.PUBLICATION_BULLETIN

    def test_default_valeurs_is_published(self):
        f = PublicationFilter()
        assert list(f.valeurs) == [PublicationStatus.PUBLISHED]

    def test_explicit_valeurs_override_default(self):
        f = PublicationFilter(valeurs=[PublicationStatus.NOT_PUBLISHED])
        assert list(f.valeurs) == [PublicationStatus.NOT_PUBLISHED]

    def test_rejects_invalid_value(self):
        with pytest.raises(ValidationError):
            _make_publication_filter(valeurs=["MAYBE"])
