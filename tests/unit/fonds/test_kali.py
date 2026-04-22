"""Unit tests for the KALI façade.

These tests target the ``pylegifrance.fonds.kali`` module at the
:meth:`LegifranceClient.call_api` boundary, mirroring the style of
``tests/unit/fonds/test_juri_verification_endpoints.py``. No live HTTP.
"""

from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.kali import (
    ConventionCollective,
    KaliAPI,
    TexteKali,
)
from pylegifrance.models.kali.enum import FacettesKALI, SortKali, TypeChampKali
from pylegifrance.models.kali.search import SearchRequest


def _mock_response(status_code: int, payload):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


def _cont_payload(cont_id: str = "KALICONT000005635384") -> dict:
    return {
        "id": cont_id,
        "titre": "Convention collective nationale du secteur exemple",
        "num": "1261",
        "numeroTexte": "IDCC 1261",
        "nature": "IDCC",
        "texteBaseId": ["KALITEXT000005677408"],
        "sections": [],
    }


def _text_payload() -> dict:
    return {
        "title": "Avenant du 12 janvier 2020",
        "etat": "VIGUEUR_ETEN",
        "typeTexte": "TEXTE_BASE",
        "idConteneur": "KALICONT000005635384",
        "nor": "ABCD1234567X",
        "articles": [],
    }


def _search_payload(ids: list[str]) -> dict:
    return {
        "totalNbResult": len(ids),
        "executionTime": 3,
        "pageNumber": 1,
        "pageSize": 10,
        "results": [{"titles": [{"id": kid}]} for kid in ids],
    }


class TestFetchContainer:
    def test_wraps_response_as_convention_collective(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _cont_payload())

        result = KaliAPI(client).fetch_container("KALICONT000005635384")

        assert isinstance(result, ConventionCollective)
        assert result.id == "KALICONT000005635384"
        assert result.idcc == "1261"
        assert result.numero_texte == "IDCC 1261"
        route, payload = client.call_api.call_args.args
        assert route == "consult/kaliCont"
        assert payload == {"id": "KALICONT000005635384"}

    def test_rejects_empty_id(self):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch_container("")


class TestFetchByIdcc:
    def test_calls_idcc_endpoint_with_normalized_id(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _cont_payload())

        KaliAPI(client).fetch_by_idcc(1261)

        route, payload = client.call_api.call_args.args
        assert route == "consult/kaliContIdcc"
        assert payload == {"id": "1261"}

    def test_rejects_non_numeric_idcc(self):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch_by_idcc("IDCC-1261")


class TestFetchText:
    def test_wraps_response_as_texte_kali(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _text_payload())

        result = KaliAPI(client).fetch_text("KALITEXT000005677408")

        assert isinstance(result, TexteKali)
        assert result.titre == "Avenant du 12 janvier 2020"
        assert result.etat == "VIGUEUR_ETEN"
        assert result.container_id == "KALICONT000005635384"
        route, payload = client.call_api.call_args.args
        assert route == "consult/kaliText"
        assert payload == {"id": "KALITEXT000005677408"}


class TestFetchDispatcher:
    @pytest.mark.parametrize(
        ("kali_id", "expected_route"),
        [
            ("KALICONT000005635384", "consult/kaliCont"),
            ("KALITEXT000005677408", "consult/kaliText"),
            ("KALIARTI000005833238", "consult/kaliArticle"),
            ("KALISCTA000005716465", "consult/kaliSection"),
        ],
    )
    def test_routes_by_prefix(self, kali_id, expected_route):
        client = MagicMock()
        payload = _cont_payload() if kali_id.startswith("KALICONT") else _text_payload()
        client.call_api.return_value = _mock_response(200, payload)

        KaliAPI(client).fetch(kali_id)

        route, _ = client.call_api.call_args.args
        assert route == expected_route

    def test_rejects_unknown_prefix(self):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch("LEGITEXT000005677408")


class TestSearch:
    def test_hydrates_results_to_texts(self):
        """The KALI /search endpoint returns KALITEXT ids in each
        ``results[i].titles[0].id``. Each result is hydrated via
        ``fetch_text`` so the return type is ``list[TexteKali]``.
        """
        client = MagicMock()
        client.call_api.side_effect = [
            _mock_response(200, _search_payload(["KALITEXT000005677408"])),
            _mock_response(200, _text_payload()),
        ]

        results = KaliAPI(client).search("santé prévoyance")

        assert len(results) == 1
        assert isinstance(results[0], TexteKali)
        assert client.call_api.call_count == 2
        # Second call must hit the kaliText endpoint, not kaliCont —
        # this is the regression guard for the 1.6.0 bug where a
        # KALITEXT id was passed to ``consult/kaliCont``, triggering
        # empty-body JSON decode failures.
        second_route = client.call_api.call_args_list[1].args[0]
        assert second_route == "consult/kaliText"

    def test_returns_empty_list_on_non_200(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(500, {})

        assert KaliAPI(client).search("x") == []

    def test_accepts_prebuilt_search_request(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _search_payload([]))

        req = SearchRequest(
            search="2098",
            field=TypeChampKali.IDCC,
            idcc="2098",
            sort=SortKali.SIGNATURE_DATE_DESC,
        )
        KaliAPI(client).search(req)

        payload = client.call_api.call_args.args[1]
        assert payload["fond"] == "KALI"
        recherche = payload["recherche"]
        assert recherche["pageSize"] == 10
        assert recherche["sort"] == "SIGNATURE_DATE_DESC"
        assert recherche["champs"][0]["typeChamp"] == "IDCC"
        assert any(
            f.get("facette") == FacettesKALI.IDCC.value and f.get("valeurs") == ["2098"]
            for f in recherche["filtres"]
        )


class TestSearchRequestToApiModel:
    def test_default_emits_fond_kali_with_all_field(self):
        dto = SearchRequest(search="salaire").to_api_model()

        assert dto.fond.value == "KALI"
        champs = dto.recherche.champs
        assert champs is not None and len(champs) == 1
        type_champ = champs[0].type_champ
        assert type_champ is not None and type_champ.value == "ALL"
        criteres = champs[0].criteres
        assert criteres is not None and criteres[0].valeur == "salaire"

    def test_default_applies_en_vigueur_filter(self):
        """Par défaut, la recherche KALI filtre aux conventions en vigueur."""
        dto = SearchRequest(search="salaire").to_api_model()
        filtres = dto.recherche.filtres
        assert filtres is not None
        legal_filters = [
            f for f in filtres if f.facette == FacettesKALI.LEGAL_STATUS.value
        ]
        assert len(legal_filters) == 1
        assert legal_filters[0].valeurs == [
            "VIGUEUR",
            "VIGUEUR_ETEN",
            "VIGUEUR_NON_ETEN",
        ]

    def test_legal_status_filter_is_materialized(self):
        req = SearchRequest(search="", legal_status=["VIGUEUR_ETEN"])
        dto = req.to_api_model()
        filtres = dto.recherche.filtres
        assert filtres is not None
        assert any(
            f.facette == FacettesKALI.LEGAL_STATUS.value
            and f.valeurs == ["VIGUEUR_ETEN"]
            for f in filtres
        )

    def test_legal_status_none_disables_filter(self):
        """``legal_status=None`` désactive le filtre par défaut."""
        dto = SearchRequest(search="", legal_status=None).to_api_model()
        filtres = dto.recherche.filtres or []
        assert not any(f.facette == FacettesKALI.LEGAL_STATUS.value for f in filtres)

    def test_legal_status_empty_list_disables_filter(self):
        """``legal_status=[]`` désactive également le filtre par défaut."""
        dto = SearchRequest(search="", legal_status=[]).to_api_model()
        filtres = dto.recherche.filtres or []
        assert not any(f.facette == FacettesKALI.LEGAL_STATUS.value for f in filtres)

    def test_invalid_date_range_rejected(self):
        with pytest.raises(ValueError):
            SearchRequest(
                search="",
                date_signature_start="2020-01-01",
                date_signature_end="2019-01-01",
            )


class TestConventionCollectiveMarkdown:
    def test_to_markdown_includes_core_metadata(self):
        cc = ConventionCollective(
            data=_cont_payload_model(),
            client=MagicMock(),
        )
        md = cc.to_markdown()
        assert "IDCC" in md
        assert "1261" in md
        assert "KALICONT000005635384" in md


def _cont_payload_model():
    from pylegifrance.models.generated.model import ConsultKaliContResponse

    return ConsultKaliContResponse.model_validate(_cont_payload())
