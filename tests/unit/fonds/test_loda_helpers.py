from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.loda import Loda


@pytest.fixture
def loda_instance():
    """Fixture pour créer une instance de Loda avec un client mock."""
    client_mock = MagicMock()
    return Loda(client_mock)


def test_extract_date_from_id_no_date(loda_instance):
    """Teste l'extraction de date quand il n'y a pas de date dans l'ID."""
    text_id = "LEGITEXT000006070721"
    base_id, date = loda_instance._extract_date_from_id(text_id)
    assert base_id == text_id
    assert date is None


def test_extract_date_from_id_with_date_iso(loda_instance):
    """Teste l'extraction de date quand l'ID contient une date au format ISO."""
    text_id = "LEGITEXT000006070721_2023-01-01"
    base_id, date = loda_instance._extract_date_from_id(text_id)
    assert base_id == "LEGITEXT000006070721"
    assert date == "2023-01-01"


def test_extract_date_from_id_with_date_fr(loda_instance):
    """Teste l'extraction de date quand l'ID contient une date au format français."""
    text_id = "LEGITEXT000006070721_01-01-2023"
    base_id, date = loda_instance._extract_date_from_id(text_id)
    assert base_id == "LEGITEXT000006070721"
    assert date == "2023-01-01"


def test_extract_date_from_id_with_invalid_date(loda_instance):
    """Teste l'extraction de date quand l'ID contient une date invalide."""
    text_id = "LEGITEXT000006070721_invalid-date"
    base_id, date = loda_instance._extract_date_from_id(text_id)
    assert base_id == "LEGITEXT000006070721"
    assert date == "invalid-date"


def test_extract_date_from_id_with_multiple_underscores(loda_instance):
    """Teste l'extraction de date quand l'ID contient plusieurs underscores."""
    text_id = "LEGITEXT000006070721_01-01-2023_extra"
    base_id, date = loda_instance._extract_date_from_id(text_id)
    assert base_id == text_id
    assert date is None
