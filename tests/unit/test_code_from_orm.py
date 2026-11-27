"""Unit tests for Code.from_orm with dict-shaped input (the shape
response.json() actually produces in CodeConsultFetcher._execute)."""

from pylegifrance.models.code.models import Code


def test_from_orm_populates_fields_from_plain_dict():
    data = {
        "id": "LEGITEXT000006070721",
        "cid": "LEGITEXT000006070721",
        "title": "Code civil",
        "etat": "VIGUEUR",
        "sections": None,
        "articles": None,
    }

    code = Code.from_orm(data)

    assert code.id == "LEGITEXT000006070721"
    assert code.title == "Code civil"
    assert code.etat == "VIGUEUR"


def test_from_orm_extracts_legitext_cid_from_titles_list():
    data = {
        "id": "LEGITEXT000006070721",
        "cid": None,
        "title": "Code civil",
        "etat": "VIGUEUR",
        "sections": None,
        "articles": None,
        "titles": [{"cid": "LEGIARTI000006419292"}, {"cid": "LEGITEXT000006070721"}],
    }

    code = Code.from_orm(data)

    assert code.cid == "LEGITEXT000006070721"
