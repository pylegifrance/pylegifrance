"""Unit tests for :class:`pylegifrance.fonds.juri.JuriDecision` behaviours not
already covered by ``test_juri_decision.py`` / ``test_to_markdown.py``:

- ``cid`` / ``eli`` / ``nor`` identifier properties
- ``date`` edge cases (string ISO parsing, invalid format, datetime passthrough)
- ``long_title``
- ``__repr__`` / ``to_dict``
- ``citations()``, ``at()``, ``latest()``, ``versions()`` (delegate to JuriAPI)
- ``to_markdown()`` branches not exercised elsewhere (missing title/id/url)
- ``_extract_plain_text()`` <br> handling

Mocks only ``LegifranceClient`` (via ``MagicMock``), never the class under
test, matching the style of ``test_juri_decision.py``.
"""

from datetime import datetime
from typing import Any
from unittest.mock import MagicMock

from pylegifrance.fonds.juri import JuriDecision
from pylegifrance.models.generated.model import TexteLien
from pylegifrance.models.juri.models import Decision


def _make_decision_with(
    *, client: MagicMock | None = None, **fields: Any
) -> JuriDecision:
    """Build a :class:`JuriDecision` with arbitrary :class:`Decision` fields.

    If ``client`` is not provided, a fresh :class:`MagicMock` is created and
    used. Callers that need to assert against the client mock after
    construction (e.g. ``call_api.assert_not_called()``) should create the
    mock themselves and pass it in, then keep their own reference to it --
    accessing it back off the constructed ``JuriDecision`` would see it
    through the ``LegifranceClient``-typed attribute instead of as a mock.
    """
    decision = Decision(**fields)
    if client is None:
        client = MagicMock()
    return JuriDecision(decision=decision, client=client)


def _make_texte_lien(**fields: Any) -> TexteLien:
    """Construct a :class:`TexteLien` via ``**kwargs`` splat.

    Routing through this helper avoids a basedpyright/pydantic interop
    limitation where passing some-but-not-all keyword arguments directly
    to a generated model's constructor makes every other field look
    required, even though they all have defaults.
    """
    return TexteLien(**fields)


class TestJuriDecisionIdentifiers:
    """cid / eli / nor properties."""

    def test_cid_returns_none_when_absent(self):
        decision = _make_decision_with(id="JURITEXT000037999394")
        assert decision.cid is None

    def test_cid_returns_validated_cid(self):
        decision = _make_decision_with(cid="JURITEXT000037999394")
        cid = decision.cid
        assert cid is not None
        assert str(cid) == "JURITEXT000037999394"

    def test_eli_returns_none_when_absent(self):
        decision = _make_decision_with(id="JURITEXT000037999394")
        assert decision.eli is None

    def test_eli_returns_validated_eli(self):
        decision = _make_decision_with(idEli="eli/juri/2020/03/04/JURITEXT000037999394")
        eli = decision.eli
        assert eli is not None
        assert str(eli) == "eli/juri/2020/03/04/JURITEXT000037999394"

    def test_nor_returns_none_when_absent(self):
        decision = _make_decision_with(id="JURITEXT000037999394")
        assert decision.nor is None

    def test_nor_returns_validated_nor(self):
        decision = _make_decision_with(nor="JUST2012345A")
        nor = decision.nor
        assert nor is not None
        assert str(nor) == "JUST2012345A"


class TestJuriDecisionDate:
    """``date`` property: str/datetime handling and invalid-format fallback."""

    def test_date_none_when_unset(self):
        decision = _make_decision_with(id="JURITEXT000037999394")
        assert decision.date is None

    def test_date_parses_datetime_value(self):
        # The generated Decision model coerces dateTexte to a real datetime,
        # so the "already a datetime" branch is what's normally hit.
        decision = _make_decision_with(dateTexte=datetime(2020, 3, 4))
        assert decision.date == datetime(2020, 3, 4)

    def test_date_parses_iso_string_via_model_construct(self):
        # Bypass validation to exercise the str branch of the `date`
        # property directly (the generated model otherwise coerces the
        # field to datetime on construction).
        decision_model = Decision.model_construct(date_texte="2020-03-04T00:00:00")
        jd = JuriDecision(decision=decision_model, client=MagicMock())
        assert jd.date == datetime(2020, 3, 4)

    def test_date_returns_none_on_invalid_string(self):
        decision_model = Decision.model_construct(date_texte="not-a-date")
        jd = JuriDecision(decision=decision_model, client=MagicMock())
        assert jd.date is None

    def test_date_returns_none_for_other_types(self):
        decision_model = Decision.model_construct(date_texte=12345)
        jd = JuriDecision(decision=decision_model, client=MagicMock())
        assert jd.date is None


class TestJuriDecisionMisc:
    def test_long_title(self):
        decision = _make_decision_with(titreLong="Cour de cassation, 4 mars 2020")
        assert decision.long_title == "Cour de cassation, 4 mars 2020"

    def test_long_title_none_when_absent(self):
        decision = _make_decision_with(id="JURITEXT000037999394")
        assert decision.long_title is None

    def test_repr_includes_id_date_and_title(self):
        decision = _make_decision_with(
            id="JURITEXT000037999394",
            titre="Arrêt du 4 mars 2020",
        )
        rendered = repr(decision)
        assert "JuriDecision(" in rendered
        assert "JURITEXT000037999394" in rendered
        assert "Arrêt du 4 mars 2020" in rendered

    def test_to_dict_returns_model_dump(self):
        decision = _make_decision_with(
            id="JURITEXT000037999394", titre="Arrêt du 4 mars 2020"
        )
        as_dict = decision.to_dict()
        assert isinstance(as_dict, dict)
        assert as_dict["id"] == "JURITEXT000037999394"
        assert as_dict["titre"] == "Arrêt du 4 mars 2020"


class TestJuriDecisionCitations:
    """``citations()`` filters liens and delegates fetching to JuriAPI."""

    def test_no_liens_returns_empty_list(self):
        decision = _make_decision_with(id="JURITEXT000037999394", liens=[])
        assert decision.citations() == []

    def test_skips_non_citation_liens(self):
        liens = [_make_texte_lien(typeLien="MODIFIE", cidTexte="JURITEXT000037999394")]
        client = MagicMock()
        decision = _make_decision_with(
            id="JURITEXT000037999394", liens=liens, client=client
        )
        assert decision.citations() == []
        client.call_api.assert_not_called()

    def test_skips_liens_with_empty_cid_texte(self):
        liens = [_make_texte_lien(typeLien="CITATION", cidTexte="")]
        client = MagicMock()
        decision = _make_decision_with(
            id="JURITEXT000037999394", liens=liens, client=client
        )
        assert decision.citations() == []
        client.call_api.assert_not_called()

    def test_skips_liens_with_missing_cid_texte(self):
        liens = [_make_texte_lien(typeLien="CITATION", cidTexte=None)]
        client = MagicMock()
        decision = _make_decision_with(
            id="JURITEXT000037999394", liens=liens, client=client
        )
        assert decision.citations() == []
        client.call_api.assert_not_called()

    def test_fetches_citation_decisions(self):
        liens = [_make_texte_lien(typeLien="CITATION", cidTexte="JURITEXT000011111111")]
        client = MagicMock()
        decision = _make_decision_with(
            id="JURITEXT000037999394", liens=liens, client=client
        )

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "text": {"id": "JURITEXT000011111111", "titre": "Autre arrêt"}
        }
        client.call_api.return_value = response

        result = decision.citations()

        assert len(result) == 1
        assert result[0].id == "JURITEXT000011111111"

    def test_exception_during_citation_fetch_is_skipped(self):
        liens = [_make_texte_lien(typeLien="CITATION", cidTexte="JURITEXT000011111111")]
        client = MagicMock()
        decision = _make_decision_with(
            id="JURITEXT000037999394", liens=liens, client=client
        )
        client.call_api.side_effect = Exception("boom")

        assert decision.citations() == []


class TestJuriDecisionAt:
    """``at()`` delegates to ``JuriAPI.fetch_version_at``."""

    def test_at_with_string_date(self):
        client = MagicMock()
        decision = _make_decision_with(id="JURITEXT000037999394", client=client)
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "text": {"id": "JURITEXT000037999394", "titre": "Version historique"}
        }
        client.call_api.return_value = response

        result = decision.at("2020-03-04")

        assert result is not None
        assert result.id == "JURITEXT000037999394"

    def test_at_with_datetime(self):
        client = MagicMock()
        decision = _make_decision_with(id="JURITEXT000037999394", client=client)
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "text": {"id": "JURITEXT000037999394", "titre": "Version historique"}
        }
        client.call_api.return_value = response

        result = decision.at(datetime(2020, 3, 4))

        assert result is not None

    def test_at_raises_on_invalid_string_date(self):
        decision = _make_decision_with(id="JURITEXT000037999394")
        import pytest

        with pytest.raises(ValueError):
            decision.at("not-a-date")

    def test_at_returns_none_when_id_missing(self):
        decision = _make_decision_with()
        assert decision.at("2020-03-04") is None

    def test_at_returns_none_on_api_exception(self):
        client = MagicMock()
        decision = _make_decision_with(id="JURITEXT000037999394", client=client)
        client.call_api.side_effect = Exception("boom")

        assert decision.at("2020-03-04") is None

    def test_at_returns_none_when_not_found(self):
        client = MagicMock()
        decision = _make_decision_with(id="JURITEXT000037999394", client=client)
        response = MagicMock()
        response.status_code = 400
        client.call_api.return_value = response

        assert decision.at("2020-03-04") is None


class TestJuriDecisionLatest:
    def test_latest_returns_none_when_id_missing(self):
        decision = _make_decision_with()
        assert decision.latest() is None

    def test_latest_delegates_to_fetch(self):
        client = MagicMock()
        decision = _make_decision_with(id="JURITEXT000037999394", client=client)
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "text": {"id": "JURITEXT000037999394", "titre": "Dernière version"}
        }
        client.call_api.return_value = response

        result = decision.latest()

        assert result is not None
        assert result.title == "Dernière version"

    def test_latest_returns_none_on_exception(self):
        client = MagicMock()
        decision = _make_decision_with(id="JURITEXT000037999394", client=client)
        client.call_api.side_effect = Exception("boom")

        assert decision.latest() is None


class TestJuriDecisionVersions:
    def test_versions_returns_empty_list_when_id_missing(self):
        decision = _make_decision_with()
        assert decision.versions() == []

    def test_versions_delegates_to_fetch_versions(self):
        client = MagicMock()
        decision = _make_decision_with(id="JURITEXT000037999394", client=client)
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = [
            {"text": {"id": "JURITEXT000037999394", "titre": "V1"}},
            {"text": {"id": "JURITEXT000037999395", "titre": "V2"}},
        ]
        client.call_api.return_value = response

        result = decision.versions()

        assert len(result) == 2
        assert {d.title for d in result} == {"V1", "V2"}

    def test_versions_returns_empty_list_on_exception(self):
        client = MagicMock()
        decision = _make_decision_with(id="JURITEXT000037999394", client=client)
        client.call_api.side_effect = Exception("boom")

        assert decision.versions() == []


class TestJuriDecisionToMarkdownBranches:
    """Branches not exercised by test_to_markdown.py: missing title/id/url."""

    def test_heading_falls_back_to_decision_literal_without_title(self):
        decision = _make_decision_with()
        rendered = decision.to_markdown()
        assert rendered.startswith("## Décision")

    def test_no_titre_line_when_title_missing(self):
        decision = _make_decision_with(
            id="JURITEXT000037999394", titre=None, solution="REJET"
        )
        rendered = decision.to_markdown()
        assert "**Titre**" not in rendered

    def test_no_reference_line_when_id_missing(self):
        decision = _make_decision_with(titre="Un arrêt")
        rendered = decision.to_markdown()
        assert "**Référence**" not in rendered

    def test_no_url_line_when_id_has_unknown_prefix(self):
        decision = _make_decision_with(id="LEGIARTI000006419292", titre="Un arrêt")
        rendered = decision.to_markdown()
        assert "**URL**" not in rendered
        assert "**Référence**: LEGIARTI000006419292" in rendered


class TestJuriDecisionExtractPlainTextBr:
    def test_br_tags_are_converted_to_newlines(self):
        decision = _make_decision_with(
            texteHtml="<p>Première ligne.<br/>Deuxième ligne.</p>"
        )
        plain = decision._extract_plain_text()
        assert plain is not None
        assert "Première ligne." in plain
        assert "Deuxième ligne." in plain
        assert "<br" not in plain
