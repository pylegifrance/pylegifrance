"""Unit tests for pylegifrance.fonds.kali filling coverage gaps left by
tests/unit/fonds/test_kali.py: domain-object property accessors,
to_dict/to_markdown/__repr__ for both ConventionCollective and TexteKali,
fetch_article/fetch_section, empty-id guards, invalid-payload handling in
_wrap_container/_wrap_text, and the less common branches of search()
(non-list results, exceptions during fetch/fetch_container, direct
ConventionCollective hits, dedupe, KALIARTI/KALISCTA hits, bad
extract_result_id shapes).
"""

from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.kali import ConventionCollective, KaliAPI, TexteKali
from pylegifrance.models.generated.model import (
    ConsultKaliContResponse,
    ConsultKaliTextResponse,
)


def _mock_response(status_code: int, payload):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


def _full_cont_payload() -> dict:
    return {
        "id": "KALICONT000005635384",
        "titre": "Convention collective nationale du secteur exemple",
        "num": "1261",
        "numeroTexte": "IDCC 1261",
        "nature": "IDCC",
        "activitePro": ["Boulangerie", "Pâtisserie"],
        "categorisation": ["Artisanat"],
        "texteBaseId": ["KALITEXT000005677408"],
        "sections": [],
    }


def _full_text_payload() -> dict:
    return {
        "title": "Avenant du 12 janvier 2020",
        "etat": "VIGUEUR_ETEN",
        "typeTexte": "TEXTE_BASE",
        "idConteneur": "KALICONT000005635384",
        "nor": "ABCD1234567X",
        "nature": "ACCORD",
        "dateTexte": "2020-01-12T00:00:00",
        "dateParution": "2020-02-01T00:00:00",
        "textNumber": "42",
        "signataires": None,
        "articles": [],
        "sections": [],
        "visasHtml": "<p>Vu la loi...</p>",
    }


class TestConventionCollectiveProperties:
    def test_all_simple_properties(self):
        cc = ConventionCollective(
            data=ConsultKaliContResponse.model_validate(_full_cont_payload()),
            client=MagicMock(),
        )
        assert cc.id == "KALICONT000005635384"
        assert cc.titre == "Convention collective nationale du secteur exemple"
        assert cc.idcc == "1261"
        assert cc.nature == "IDCC"
        assert cc.numero_texte == "IDCC 1261"
        assert cc.activites_pro == ["Boulangerie", "Pâtisserie"]
        assert cc.categorisation == ["Artisanat"]
        assert cc.texte_base_ids == ["KALITEXT000005677408"]
        assert cc.sections == []

    def test_sections_defaults_to_empty_list_when_none(self):
        data = ConsultKaliContResponse.model_validate({"id": "KALICONT1"})
        cc = ConventionCollective(data=data, client=MagicMock())
        assert cc.sections == []

    def test_to_dict_round_trips_aliases(self):
        cc = ConventionCollective(
            data=ConsultKaliContResponse.model_validate(_full_cont_payload()),
            client=MagicMock(),
        )
        d = cc.to_dict()
        assert d["id"] == "KALICONT000005635384"
        assert d["texteBaseId"] == ["KALITEXT000005677408"]

    def test_to_markdown_includes_all_present_fields(self):
        cc = ConventionCollective(
            data=ConsultKaliContResponse.model_validate(_full_cont_payload()),
            client=MagicMock(),
        )
        md = cc.to_markdown()
        assert "**IDCC**: 1261" in md
        assert "**Numéro**: IDCC 1261" in md
        assert "**Nature**: IDCC" in md
        assert "**Activités**: Boulangerie, Pâtisserie" in md
        assert "**Référence**: KALICONT000005635384" in md

    def test_to_markdown_falls_back_to_id_when_no_titre(self):
        data = ConsultKaliContResponse.model_validate({"id": "KALICONT1"})
        cc = ConventionCollective(data=data, client=MagicMock())
        assert "## KALICONT1" in cc.to_markdown()

    def test_to_markdown_default_heading_when_nothing_set(self):
        data = ConsultKaliContResponse.model_validate({})
        cc = ConventionCollective(data=data, client=MagicMock())
        assert "## Convention collective" in cc.to_markdown()

    def test_repr(self):
        cc = ConventionCollective(
            data=ConsultKaliContResponse.model_validate(_full_cont_payload()),
            client=MagicMock(),
        )
        r = repr(cc)
        assert "ConventionCollective(" in r
        assert "KALICONT000005635384" in r
        assert "1261" in r


class TestTexteKaliProperties:
    def test_all_simple_properties(self):
        text = TexteKali(
            data=ConsultKaliTextResponse.model_validate(_full_text_payload()),
            client=MagicMock(),
        )
        assert text.titre == "Avenant du 12 janvier 2020"
        assert text.nor == "ABCD1234567X"
        assert text.etat == "VIGUEUR_ETEN"
        assert text.type_texte == "TEXTE_BASE"
        assert text.nature == "ACCORD"
        assert text.date_signature is not None
        assert text.date_parution is not None
        assert text.texte_numero == "42"
        assert text.signataires is None
        assert text.articles == []
        assert text.sections == []
        assert text.visas_html == "<p>Vu la loi...</p>"
        assert text.container_id == "KALICONT000005635384"

    def test_articles_and_sections_default_to_empty_list(self):
        data = ConsultKaliTextResponse.model_validate({"title": "Texte minimal"})
        text = TexteKali(data=data, client=MagicMock())
        assert text.articles == []
        assert text.sections == []

    def test_to_dict_round_trips_aliases(self):
        text = TexteKali(
            data=ConsultKaliTextResponse.model_validate(_full_text_payload()),
            client=MagicMock(),
        )
        d = text.to_dict()
        assert d["title"] == "Avenant du 12 janvier 2020"
        assert d["idConteneur"] == "KALICONT000005635384"

    def test_to_markdown_includes_all_present_fields(self):
        text = TexteKali(
            data=ConsultKaliTextResponse.model_validate(_full_text_payload()),
            client=MagicMock(),
        )
        md = text.to_markdown()
        assert "**Statut**: VIGUEUR_ETEN" in md
        assert "**Type**: TEXTE_BASE" in md
        assert "**NOR**: ABCD1234567X" in md
        assert "**Numéro**: 42" in md
        assert "**Signé le**:" in md
        assert "**Paru le**:" in md
        assert "**Conteneur**: KALICONT000005635384" in md

    def test_to_markdown_default_heading_when_nothing_set(self):
        data = ConsultKaliTextResponse.model_validate({})
        text = TexteKali(data=data, client=MagicMock())
        assert "## Texte KALI" in text.to_markdown()

    def test_repr(self):
        text = TexteKali(
            data=ConsultKaliTextResponse.model_validate(_full_text_payload()),
            client=MagicMock(),
        )
        r = repr(text)
        assert "TexteKali(" in r
        assert "VIGUEUR_ETEN" in r
        assert "KALICONT000005635384" in r


class TestFetchContainerEdgeCases:
    def test_returns_none_on_empty_response(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, {})

        result = KaliAPI(client).fetch_container("KALICONT000005635384")

        assert result is None

    def test_returns_none_on_null_response(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, None)

        assert KaliAPI(client).fetch_container("KALICONT000005635384") is None

    def test_returns_none_on_validation_error(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200, {"executionTime": "not-an-int"}
        )

        assert KaliAPI(client).fetch_container("KALICONT000005635384") is None

    def test_rejects_whitespace_only_id(self):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch_container("   ")


class TestFetchByIdccValidation:
    @pytest.mark.parametrize("idcc", ["1", "12", "123", "1234", "12345", 1261])
    def test_accepts_one_to_five_digits(self, idcc):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _full_cont_payload())

        KaliAPI(client).fetch_by_idcc(idcc)

        route, payload = client.call_api.call_args.args
        assert route == "consult/kaliContIdcc"
        assert payload == {"id": str(idcc)}

    @pytest.mark.parametrize("idcc", ["123456", "", "12a", "IDCC1261", "-1"])
    def test_rejects_invalid_formats(self, idcc):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch_by_idcc(idcc)


class TestFetchTextEdgeCases:
    def test_rejects_empty_id(self):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch_text("")

    def test_rejects_whitespace_only_id(self):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch_text("   ")

    def test_returns_none_on_empty_response(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, {})

        assert KaliAPI(client).fetch_text("KALITEXT000005677408") is None

    def test_returns_none_on_validation_error(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, {"dateTexte": "not-a-date"})

        assert KaliAPI(client).fetch_text("KALITEXT000005677408") is None


class TestFetchArticle:
    def test_wraps_response_as_texte_kali(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _full_text_payload())

        result = KaliAPI(client).fetch_article("KALIARTI000005833238")

        assert isinstance(result, TexteKali)
        route, payload = client.call_api.call_args.args
        assert route == "consult/kaliArticle"
        assert payload == {"id": "KALIARTI000005833238"}

    def test_rejects_empty_id(self):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch_article("")

    def test_rejects_whitespace_only_id(self):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch_article("   ")

    def test_returns_none_when_not_found(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, {})

        assert KaliAPI(client).fetch_article("KALIARTI000005833238") is None


class TestFetchSection:
    def test_wraps_response_as_texte_kali(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _full_text_payload())

        result = KaliAPI(client).fetch_section("KALISCTA000005716465")

        assert isinstance(result, TexteKali)
        route, payload = client.call_api.call_args.args
        assert route == "consult/kaliSection"
        assert payload == {"id": "KALISCTA000005716465"}

    def test_rejects_empty_id(self):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch_section("")

    def test_rejects_whitespace_only_id(self):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch_section("   ")

    def test_returns_none_when_not_found(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, {})

        assert KaliAPI(client).fetch_section("KALISCTA000005716465") is None


class TestFetchDispatcherEdgeCases:
    def test_rejects_empty_id(self):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch("")

    def test_rejects_whitespace_only_id(self):
        with pytest.raises(ValueError):
            KaliAPI(MagicMock()).fetch("   ")

    def test_rejects_unknown_prefix_message_lists_known_prefixes(self):
        with pytest.raises(ValueError, match="KALICONT"):
            KaliAPI(MagicMock()).fetch("JORFTEXT000005677408")


def _search_payload(ids: list[str]) -> dict:
    return {
        "totalNbResult": len(ids),
        "executionTime": 3,
        "pageNumber": 1,
        "pageSize": 10,
        "results": [{"titles": [{"id": kid}]} for kid in ids],
    }


class TestSearchEdgeCases:
    def test_returns_empty_list_when_results_not_a_list(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200,
            {
                "totalNbResult": 0,
                "executionTime": 1,
                "pageNumber": 1,
                "pageSize": 10,
                "results": "not-a-list",
            },
        )

        assert KaliAPI(client).search("x") == []

    def test_returns_empty_list_when_results_key_missing(self):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200,
            {"totalNbResult": 0, "executionTime": 1, "pageNumber": 1, "pageSize": 10},
        )

        assert KaliAPI(client).search("x") == []

    @pytest.mark.parametrize(
        "result",
        [
            {},
            {"titles": "not-a-list"},
            {"titles": []},
            {"titles": ["not-a-dict"]},
            {"titles": [{"id": None}]},
            {"titles": [{"id": ""}]},
            {"titles": [{}]},
        ],
    )
    def test_skips_results_with_unresolvable_id(self, result):
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200,
            {
                "totalNbResult": 1,
                "executionTime": 1,
                "pageNumber": 1,
                "pageSize": 10,
                "results": [result],
            },
        )

        assert KaliAPI(client).search("x") == []
        # No follow-up fetch() call since the id could not be extracted.
        assert client.call_api.call_count == 1

    def test_hydrates_direct_kalicont_search_hits(self):
        client = MagicMock()
        client.call_api.side_effect = [
            _mock_response(200, _search_payload(["KALICONT000005635384"])),
            _mock_response(200, _full_cont_payload()),
        ]

        results = KaliAPI(client).search("x")

        assert len(results) == 1
        assert isinstance(results[0], ConventionCollective)
        assert results[0].id == "KALICONT000005635384"

    def test_deduplicates_direct_kalicont_hits(self):
        client = MagicMock()
        client.call_api.side_effect = [
            _mock_response(
                200,
                _search_payload(["KALICONT000005635384", "KALICONT000005635384"]),
            ),
            _mock_response(200, _full_cont_payload()),
            _mock_response(200, _full_cont_payload()),
        ]

        results = KaliAPI(client).search("x")

        assert len(results) == 1
        # /search + 2 x /consult/kaliCont (fetch() doesn't dedupe before
        # fetching; dedupe only drops the already-seen result afterwards).
        assert client.call_api.call_count == 3

    def test_skips_container_hit_with_no_id(self):
        client = MagicMock()
        client.call_api.side_effect = [
            _mock_response(200, _search_payload(["KALICONT000005635384"])),
            # Non-empty payload (truthy, passes the _wrap_container falsy
            # check) but with no "id" field -> entity.id is None, so the
            # "not cont_id" branch is exercised rather than "entity is None".
            _mock_response(200, {"titre": "Sans identifiant"}),
        ]

        assert KaliAPI(client).search("x") == []

    def test_fetch_exception_is_logged_and_skipped(self):
        client = MagicMock()
        client.call_api.side_effect = [
            _mock_response(200, _search_payload(["KALICONT000005635384"])),
            RuntimeError("boom"),
        ]

        assert KaliAPI(client).search("x") == []

    def test_fetch_container_exception_during_text_resolution_is_skipped(self):
        client = MagicMock()
        client.call_api.side_effect = [
            _mock_response(200, _search_payload(["KALITEXT000005677408"])),
            _mock_response(200, _full_text_payload()),
            RuntimeError("boom"),
        ]

        assert KaliAPI(client).search("x") == []

    def test_text_hit_dedup_skips_already_seen_container(self):
        client = MagicMock()
        client.call_api.side_effect = [
            _mock_response(
                200,
                _search_payload(["KALICONT000005635384", "KALITEXT000005677408"]),
            ),
            _mock_response(200, _full_cont_payload()),
            _mock_response(200, _full_text_payload()),  # container_id == same id
        ]

        results = KaliAPI(client).search("x")

        assert len(results) == 1
        # /search, /consult/kaliCont (direct hit), /consult/kaliText
        # (second hit) -- no second /consult/kaliCont since the parent
        # container id was already seen via the first hit.
        assert client.call_api.call_count == 3

    def test_direct_kalicont_hit_resolving_to_none_is_skipped(self):
        """entity is None after fetch() succeeds (not an exception): the
        container consult call returns an empty payload."""
        client = MagicMock()
        client.call_api.side_effect = [
            _mock_response(200, _search_payload(["KALICONT000005635384"])),
            _mock_response(200, {}),  # _wrap_container returns None
        ]

        assert KaliAPI(client).search("x") == []

    def test_text_hit_whose_resolved_container_is_none_is_skipped(self):
        """TexteKali branch: fetch_container succeeds (no exception) but
        resolves to None because the container payload is empty."""
        client = MagicMock()
        client.call_api.side_effect = [
            _mock_response(200, _search_payload(["KALITEXT000005677408"])),
            _mock_response(200, _full_text_payload()),
            _mock_response(200, {}),  # fetch_container -> None
        ]

        assert KaliAPI(client).search("x") == []


class TestTexteKaliContainerIdFallbackEdgeCase:
    def test_falls_through_to_none_when_conteneurs_first_cid_is_empty(self):
        """`conteneurs[0]` present but its `cid` is falsy: container_id
        must fall through to None rather than returning the falsy value."""
        payload = dict(_full_text_payload())
        payload["idConteneur"] = None
        payload["conteneurs"] = [{"cid": ""}]
        data = ConsultKaliTextResponse.model_validate(payload)

        text = TexteKali(data=data, client=MagicMock())

        assert text.container_id is None
