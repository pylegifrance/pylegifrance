"""Unit tests for the JuriAPI verification endpoints.

These cover three methods added to :class:`pylegifrance.fonds.juri.JuriAPI`
that expose Legifrance endpoints used to deterministically verify case-law
citations:

- :meth:`JuriAPI.fetch_by_id` — canonical POST /consult/juri
- :meth:`JuriAPI.search_by_ecli` — POST /search with typeChamp=ECLI
- :meth:`JuriAPI.search_by_affaire` — POST /search with NUM_AFFAIRE +
  CASSATION_FORMATION + DATE_DECISION filters

Tests mock the :meth:`LegifranceClient.call_api` boundary only; they do not
stub or monkey-patch the HTTP transport itself. This mirrors the existing
unit-test style in ``tests/unit/fonds/test_juri_decision.py``.
"""

from datetime import date
from unittest.mock import MagicMock

import pytest

from pylegifrance.fonds.juri import JuriAPI, JuriDecision


def _mock_response(status_code: int, payload):
    """Build a minimal stand-in for a ``requests.Response``."""
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


def _consult_payload(text_id: str | None = "JURITEXT000037999394") -> dict:
    """Build a realistic ``POST /consult/juri`` response body.

    The body shape follows what :class:`ConsultResponse.from_api_model`
    consumes: a top-level ``text`` object containing a populated decision.
    """
    if text_id is None:
        return {"text": None, "executionTime": 12}
    return {
        "text": {
            "id": text_id,
            "titre": "Arrêt du 4 mars 2020",
            "titreLong": "Cour de cassation, Chambre sociale, 4 mars 2020",
            "liens": [],
        },
        "executionTime": 12,
    }


def _search_payload(ids: list[str]) -> dict:
    """Build a realistic ``POST /search`` response body.

    Matches the path walked by ``JuriAPI.search`` and our new
    ``_run_search_dto``: ``results[].titles[0].id``.
    """
    return {
        "totalNbResult": len(ids),
        "executionTime": 5,
        "pageNumber": 1,
        "pageSize": 10,
        "results": [{"titles": [{"id": text_id}]} for text_id in ids],
    }


class TestFetchById:
    """Unit tests for :meth:`JuriAPI.fetch_by_id`."""

    def test_returns_juri_decision_when_text_exists(self):
        """Happy path: API returns a populated text, method wraps it."""
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200, _consult_payload("JURITEXT000037999394")
        )

        decision = JuriAPI(client).fetch_by_id("JURITEXT000037999394")

        assert isinstance(decision, JuriDecision)
        assert decision.id == "JURITEXT000037999394"

        # Verify we hit the correct route and that the body contains only
        # ``{"textId": ...}`` (no dangling ``searchedString: null``).
        call_args = client.call_api.call_args
        assert call_args.args[0] == "consult/juri"
        body = call_args.args[1]
        assert body == {"textId": "JURITEXT000037999394"}

    def test_returns_none_when_text_field_empty(self):
        """Legifrance answers 200 but with an empty text → decision absent.

        This is a defensive path: in practice the live ``/consult/juri``
        endpoint returns HTTP 400 for unknown ids rather than an empty 200,
        but if DILA ever changes that behaviour (or an intermediate cache
        serves an empty body), the method must still degrade to ``None``
        instead of raising.
        """
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _consult_payload(None))

        decision = JuriAPI(client).fetch_by_id("JURITEXT000000000000")

        assert decision is None

    def test_returns_none_on_unknown_text_id_400(self):
        """Legifrance's HTTP 400 "unknown textId" signature maps to ``None``.

        The live ``/consult/juri`` endpoint answers HTTP 400 with the body
        ``"L'expression à valider est fausse"`` for well-formed-but-unknown
        JURITEXT/CETATEXT ids. ``fetch_by_id`` MUST recognise that specific
        signature and return ``None`` instead of propagating the wrapped
        ``Exception`` — otherwise callers cannot distinguish "does not
        exist" from "could not verify".
        """
        client = MagicMock()
        client.call_api.side_effect = Exception(
            "API client error 400 - "
            '{"timestamp":1776183476285,"error":400,"status":"Bad Request",'
            '"message":"L\'expression à valider est fausse.",'
            '"errorCode":null,"exceptionDetails":null}'
        )

        decision = JuriAPI(client).fetch_by_id("JURITEXT099999999999")

        assert decision is None

    def test_raises_value_error_on_empty_identifier(self):
        """An empty ``text_id`` is a programming error, not an unknown id."""
        client = MagicMock()

        with pytest.raises(ValueError):
            JuriAPI(client).fetch_by_id("")

        with pytest.raises(ValueError):
            JuriAPI(client).fetch_by_id("   ")

        client.call_api.assert_not_called()

    @pytest.mark.parametrize(
        "bad_id",
        [
            "FOO",
            "JURITEXT",
            "JURITEXT12345",
            "JURITEXT0000000000000",  # 13 digits
            "JURITEXT00000000000",  # 11 digits
            "juritext000037999394",  # lowercase prefix
            "JURITEXT00003799939A",  # non-numeric suffix
            "FOOTEXT000037999394",
            "JURITEXT 000037999394",  # internal whitespace
        ],
    )
    def test_raises_value_error_on_malformed_format(self, bad_id):
        """Client-side format validation rejects malformed ids up front.

        The canonical Legifrance case-law textId is either ``JURITEXT`` or
        ``CETATEXT`` followed by exactly 12 numeric digits. Anything else
        is rejected BEFORE any network round-trip so the caller gets a
        precise :class:`ValueError` instead of a cryptic server-side 400.
        """
        client = MagicMock()

        with pytest.raises(ValueError, match="Invalid text_id format"):
            JuriAPI(client).fetch_by_id(bad_id)

        client.call_api.assert_not_called()

    def test_accepts_cetat_text_id(self):
        """CETATEXT ids (Conseil d'État) are just as valid as JURITEXT."""
        client = MagicMock()
        client.call_api.return_value = _mock_response(
            200, _consult_payload("CETATEXT000007422435")
        )

        decision = JuriAPI(client).fetch_by_id("CETATEXT000007422435")

        assert isinstance(decision, JuriDecision)
        assert decision.id == "CETATEXT000007422435"

    def test_transport_error_propagates(self):
        """Transport/auth/5xx failures must NOT be swallowed as 'not found'.

        The whole point of ``fetch_by_id`` as a verifier is to let the
        caller distinguish 'Legifrance says this does not exist' from 'we
        could not reach Legifrance'. Returning ``None`` in both cases
        would defeat the contract.
        """
        client = MagicMock()
        client.call_api.side_effect = Exception("API client error 500 - boom")

        with pytest.raises(Exception, match="API client error 500"):
            JuriAPI(client).fetch_by_id("JURITEXT000037999394")

    def test_unrelated_400_propagates(self):
        """A 400 that is NOT the "unknown textId" signature still propagates.

        We only translate the specific ``"L'expression à valider est
        fausse"`` marker to ``None``; any other 400 (schema error, missing
        field, auth envelope issue, ...) is still a caller-visible failure.
        """
        client = MagicMock()
        client.call_api.side_effect = Exception(
            "API client error 400 - Bad Request: malformed JSON body"
        )

        with pytest.raises(Exception, match="400"):
            JuriAPI(client).fetch_by_id("JURITEXT000037999394")


class TestSearchByEcli:
    """Unit tests for :meth:`JuriAPI.search_by_ecli`."""

    def test_happy_path_hydrates_matches(self):
        """A matching ECLI resolves to a hydrated JuriDecision list."""
        client = MagicMock()

        def side_effect(route: str, data):
            if route == "search":
                return _mock_response(200, _search_payload(["JURITEXT000036721234"]))
            if route == "consult/juri":
                return _mock_response(200, _consult_payload("JURITEXT000036721234"))
            raise AssertionError(f"unexpected route: {route}")

        client.call_api.side_effect = side_effect

        matches = JuriAPI(client).search_by_ecli("ECLI:FR:CCASS:2018:CO00579")

        assert len(matches) == 1
        assert matches[0].id == "JURITEXT000036721234"

        # Inspect the search request body to verify the field search.
        search_call = client.call_api.call_args_list[0]
        assert search_call.args[0] == "search"
        body = search_call.args[1]
        assert body["fond"] == "JURI"
        champs = body["recherche"]["champs"]
        assert len(champs) == 1
        assert champs[0]["typeChamp"] == "ECLI"
        assert champs[0]["criteres"][0]["valeur"] == "ECLI:FR:CCASS:2018:CO00579"
        assert champs[0]["criteres"][0]["typeRecherche"] == "EXACTE"

    def test_empty_results_returns_empty_list(self):
        """Unknown ECLI → search endpoint returns no results → [] list."""
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _search_payload([]))

        matches = JuriAPI(client).search_by_ecli("ECLI:FR:CCASS:2099:XX99999")

        assert matches == []

    def test_accepts_cetat_fond(self):
        """Callers can search the Conseil d'État corpus via fond=CETAT."""
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _search_payload([]))

        JuriAPI(client).search_by_ecli("ECLI:FR:CE:2024:123456.20240101", fond="CETAT")

        body = client.call_api.call_args.args[1]
        assert body["fond"] == "CETAT"

    def test_rejects_unknown_fond(self):
        """Unknown fonds raise ValueError — do not silently fall through."""
        client = MagicMock()

        with pytest.raises(ValueError, match="Fond non supporté"):
            JuriAPI(client).search_by_ecli("ECLI:FR:CCASS:2018:CO00579", fond="KALI")

        client.call_api.assert_not_called()

    def test_rejects_empty_ecli(self):
        """Empty ECLIs are a programming error."""
        client = MagicMock()

        with pytest.raises(ValueError):
            JuriAPI(client).search_by_ecli("")

        client.call_api.assert_not_called()

    def test_transport_error_propagates(self):
        """Transport failures bubble up from the search endpoint too."""
        client = MagicMock()
        client.call_api.side_effect = Exception("API client error 502 - bad gateway")

        with pytest.raises(Exception, match="502"):
            JuriAPI(client).search_by_ecli("ECLI:FR:CCASS:2018:CO00579")


class TestSearchByAffaire:
    """Unit tests for :meth:`JuriAPI.search_by_affaire`."""

    def test_happy_path_with_formation_and_exact_date(self):
        """Canonical Cassation tuple: num + formation alias + date."""
        client = MagicMock()

        def side_effect(route: str, data):
            if route == "search":
                return _mock_response(200, _search_payload(["JURITEXT000041234567"]))
            if route == "consult/juri":
                return _mock_response(200, _consult_payload("JURITEXT000041234567"))
            raise AssertionError(f"unexpected route: {route}")

        client.call_api.side_effect = side_effect

        matches = JuriAPI(client).search_by_affaire(
            num_affaire="18-26.218",
            formation="Soc",
            date_decision=date(2020, 3, 4),
        )

        assert len(matches) == 1
        assert matches[0].id == "JURITEXT000041234567"

        search_body = client.call_api.call_args_list[0].args[1]
        assert search_body["fond"] == "JURI"
        champs = search_body["recherche"]["champs"]
        assert champs[0]["typeChamp"] == "NUM_AFFAIRE"
        assert champs[0]["criteres"][0]["valeur"] == "18-26.218"
        assert champs[0]["criteres"][0]["typeRecherche"] == "EXACTE"

        filtres = search_body["recherche"]["filtres"]
        facettes = {f["facette"] for f in filtres}
        assert "CASSATION_FORMATION" in facettes
        assert "DATE_DECISION" in facettes

        formation_filter = next(
            f for f in filtres if f["facette"] == "CASSATION_FORMATION"
        )
        # Alias "Soc" must be resolved to the canonical Legifrance label.
        assert formation_filter["valeurs"] == ["Chambre sociale"]

        date_filter = next(f for f in filtres if f["facette"] == "DATE_DECISION")
        assert date_filter["dates"] is not None
        assert "2020-03-04" in str(date_filter["dates"]["start"])
        assert "2020-03-04" in str(date_filter["dates"]["end"])

    def test_passthrough_for_unknown_formation(self):
        """Unknown formation strings are forwarded verbatim to Legifrance."""
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _search_payload([]))

        JuriAPI(client).search_by_affaire(
            num_affaire="20-80.000",
            formation="Chambre sociale",
        )

        body = client.call_api.call_args.args[1]
        formation_filter = next(
            f
            for f in body["recherche"]["filtres"]
            if f["facette"] == "CASSATION_FORMATION"
        )
        assert formation_filter["valeurs"] == ["Chambre sociale"]

    def test_date_range_filter(self):
        """A ``date_range`` builds an inclusive DATE_DECISION DatePeriod."""
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _search_payload([]))

        JuriAPI(client).search_by_affaire(
            num_affaire="18-26.218",
            date_range=(date(2020, 1, 1), date(2020, 12, 31)),
        )

        body = client.call_api.call_args.args[1]
        date_filter = next(
            f for f in body["recherche"]["filtres"] if f["facette"] == "DATE_DECISION"
        )
        assert "2020-01-01" in str(date_filter["dates"]["start"])
        assert "2020-12-31" in str(date_filter["dates"]["end"])

    def test_rejects_empty_num_affaire(self):
        client = MagicMock()

        with pytest.raises(ValueError):
            JuriAPI(client).search_by_affaire(num_affaire="")

        client.call_api.assert_not_called()

    def test_rejects_both_date_modes(self):
        """date_decision and date_range are mutually exclusive."""
        client = MagicMock()

        with pytest.raises(ValueError, match="incompatibles"):
            JuriAPI(client).search_by_affaire(
                num_affaire="18-26.218",
                date_decision=date(2020, 3, 4),
                date_range=(date(2020, 1, 1), date(2020, 12, 31)),
            )

        client.call_api.assert_not_called()

    def test_rejects_inverted_date_range(self):
        """end < start is almost always a caller bug → raise ValueError."""
        client = MagicMock()

        with pytest.raises(ValueError, match=">="):
            JuriAPI(client).search_by_affaire(
                num_affaire="18-26.218",
                date_range=(date(2020, 12, 31), date(2020, 1, 1)),
            )

        client.call_api.assert_not_called()

    def test_empty_result_set(self):
        """Search endpoint returning zero hits yields an empty list."""
        client = MagicMock()
        client.call_api.return_value = _mock_response(200, _search_payload([]))

        matches = JuriAPI(client).search_by_affaire(num_affaire="99-99.999")

        assert matches == []

    def test_transport_error_propagates(self):
        """Transport errors from the search call bubble up."""
        client = MagicMock()
        client.call_api.side_effect = Exception("API client error 503 - down")

        with pytest.raises(Exception, match="503"):
            JuriAPI(client).search_by_affaire(num_affaire="18-26.218")
