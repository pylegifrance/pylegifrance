"""Unit tests for :class:`pylegifrance.models.loda.models.TexteLoda`.

Pure model tests covering every property delegating to the wrapped
``ConsultTextResponse`` (both when ``consult_response`` is set and when it
is ``None``), the ``etat``/``juris_state`` fallback, and the ``_dt`` date
conversion helpers (valid ISO strings, ``Z`` suffix handling, invalid
strings, and ``None`` inputs).
"""

from datetime import datetime
from typing import Any

from pylegifrance.models.generated.model import ConsultTextResponse
from pylegifrance.models.loda.models import TexteLoda


def _make_texte_loda(**fields: Any) -> TexteLoda:
    """Construct a :class:`TexteLoda` via ``**kwargs`` splat.

    Routing through this helper avoids a basedpyright/pydantic interop
    limitation where passing some-but-not-all keyword arguments directly
    to a generated model's constructor makes every other field look
    required, even though they all have defaults.
    """
    return TexteLoda(**fields)


def _full_response() -> ConsultTextResponse:
    return ConsultTextResponse.model_validate(
        {
            "id": "LEGITEXT000006070721_01-01-2021",
            "cid": "LEGITEXT000006070721",
            "title": "Code civil",
            "dateDebutVersion": "2021-01-01",
            "dateFinVersion": "2021-12-31",
            "etat": "VIGUEUR",
            "sections": [],
            "nor": "JUSC2011622L",
            "dossiersLegislatifs": [],
            "nature": "CODE",
            "resume": "Résumé du texte",
            "visa": "Vu la Constitution...",
            "signers": "Le Président de la République",
            "nota": "Nota important",
            "observations": "Observations diverses",
            "dateTexte": "2020-06-17T00:00:00",
            "textAbroge": False,
            "articles": [],
        }
    )


class TestPropertiesWithConsultResponse:
    def test_id(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.id == "LEGITEXT000006070721_01-01-2021"

    def test_cid(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.cid == "LEGITEXT000006070721"

    def test_titre(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.titre == "Code civil"

    def test_date_debut(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.date_debut == "2021-01-01"

    def test_date_fin(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.date_fin == "2021-12-31"

    def test_etat_uses_etat_field_when_present(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.etat == "VIGUEUR"

    def test_etat_falls_back_to_juris_state(self):
        response = ConsultTextResponse.model_validate(
            {"etat": None, "jurisState": "ABROGE"}
        )
        texte = _make_texte_loda(consult_response=response)
        assert texte.etat == "ABROGE"

    def test_etat_is_none_when_neither_field_set(self):
        response = ConsultTextResponse.model_validate({})
        texte = _make_texte_loda(consult_response=response)
        assert texte.etat is None

    def test_sections(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.sections == []

    def test_nor(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.nor == "JUSC2011622L"

    def test_dossiers_legislatifs(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.dossiers_legislatifs == []

    def test_nature(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.nature == "CODE"

    def test_resume(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.resume == "Résumé du texte"

    def test_visa(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.visa == "Vu la Constitution..."

    def test_signers(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.signers == "Le Président de la République"

    def test_nota(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.nota == "Nota important"

    def test_observations(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.observations == "Observations diverses"

    def test_date_texte(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.date_texte == datetime(2020, 6, 17)

    def test_text_abroge(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.text_abroge is False

    def test_articles(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.articles == []


class TestPropertiesWithoutConsultResponse:
    """Every delegated property must degrade to None when consult_response
    is unset, instead of raising AttributeError."""

    def test_all_properties_return_none(self):
        texte = _make_texte_loda()
        assert texte.id is None
        assert texte.cid is None
        assert texte.titre is None
        assert texte.date_debut is None
        assert texte.date_fin is None
        assert texte.etat is None
        assert texte.sections is None
        assert texte.nor is None
        assert texte.dossiers_legislatifs is None
        assert texte.nature is None
        assert texte.resume is None
        assert texte.visa is None
        assert texte.signers is None
        assert texte.nota is None
        assert texte.observations is None
        assert texte.date_texte is None
        assert texte.text_abroge is None
        assert texte.articles is None


class TestDateConversionHelpers:
    def test_date_debut_dt_parses_iso_string(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.date_debut_dt == datetime(2021, 1, 1)

    def test_date_debut_dt_is_none_when_date_debut_is_none(self):
        texte = _make_texte_loda(
            consult_response=ConsultTextResponse.model_validate({})
        )
        assert texte.date_debut_dt is None

    def test_date_debut_dt_handles_z_suffix(self):
        response = ConsultTextResponse.model_validate(
            {"dateDebutVersion": "2021-01-01T00:00:00Z"}
        )
        texte = _make_texte_loda(consult_response=response)
        assert texte.date_debut_dt is not None
        assert texte.date_debut_dt.year == 2021

    def test_date_debut_dt_returns_none_on_invalid_string(self):
        response = ConsultTextResponse.model_validate(
            {"dateDebutVersion": "not-a-date"}
        )
        texte = _make_texte_loda(consult_response=response)
        assert texte.date_debut_dt is None

    def test_date_fin_dt_parses_iso_string(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.date_fin_dt == datetime(2021, 12, 31)

    def test_date_fin_dt_is_none_when_date_fin_is_none(self):
        texte = _make_texte_loda(
            consult_response=ConsultTextResponse.model_validate({})
        )
        assert texte.date_fin_dt is None

    def test_date_fin_dt_returns_none_on_invalid_string(self):
        response = ConsultTextResponse.model_validate({"dateFinVersion": "nope"})
        texte = _make_texte_loda(consult_response=response)
        assert texte.date_fin_dt is None

    def test_last_update_dt_parses_iso_string(self):
        texte = _make_texte_loda(last_update="2022-05-01T10:00:00")
        assert texte.last_update_dt == datetime(2022, 5, 1, 10, 0, 0)

    def test_last_update_dt_is_none_when_last_update_is_none(self):
        texte = _make_texte_loda()
        assert texte.last_update_dt is None

    def test_last_update_dt_returns_none_on_invalid_string(self):
        texte = _make_texte_loda(last_update="garbage")
        assert texte.last_update_dt is None

    def test_date_texte_dt_mirrors_date_texte(self):
        texte = _make_texte_loda(consult_response=_full_response())
        assert texte.date_texte_dt == texte.date_texte == datetime(2020, 6, 17)

    def test_date_texte_dt_is_none_without_consult_response(self):
        texte = _make_texte_loda()
        assert texte.date_texte_dt is None


class TestOwnFields:
    def test_titre_long_and_texte_html_default_to_none(self):
        texte = _make_texte_loda()
        assert texte.titre_long is None
        assert texte.texte_html is None

    def test_titre_long_and_texte_html_can_be_set(self):
        texte = _make_texte_loda(
            titre_long="Titre complet", texte_html="<p>contenu</p>"
        )
        assert texte.titre_long == "Titre complet"
        assert texte.texte_html == "<p>contenu</p>"
