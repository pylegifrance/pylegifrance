"""Unit tests for JudilibreDecision property accessors, to_markdown(), and
the url fallback branches not covered by test_judilibre_decision.py.
"""

from pylegifrance.fonds.judilibre import JudilibreDecision
from pylegifrance.models.judilibre.models import DecisionFull


def _full_decision(**overrides) -> DecisionFull:
    data = {
        "id": "abc123",
        "jurisdiction": "Cour de cassation",
        "chamber": "Chambre sociale",
        "ecli": "ECLI:FR:CCASS:2020:SO00304",
        "decision_date": "2020-03-04",
        "summary": "Résumé de la décision",
        "solution": "Rejet",
        "text": "Texte intégral de la décision.",
        "update_date": "2020-03-10",
        "files": None,
    }
    data.update(overrides)
    return DecisionFull(**data)


# ---------------------------------------------------------------------------
# Property accessors
# ---------------------------------------------------------------------------


def test_properties_reflect_underlying_decision_fields():
    decision = JudilibreDecision(_full_decision())

    assert decision.jurisdiction == "Cour de cassation"
    assert decision.chamber == "Chambre sociale"
    assert decision.ecli == "ECLI:FR:CCASS:2020:SO00304"
    assert decision.decision_date == "2020-03-04"
    assert decision.summary == "Résumé de la décision"
    assert decision.solution == "Rejet"
    assert decision.text == "Texte intégral de la décision."
    assert decision.update_date == "2020-03-10"


def test_properties_are_none_when_fields_unset():
    decision = JudilibreDecision(
        _full_decision(
            jurisdiction=None,
            chamber=None,
            ecli=None,
            decision_date=None,
            summary=None,
            solution=None,
            text=None,
            update_date=None,
        )
    )

    assert decision.jurisdiction is None
    assert decision.chamber is None
    assert decision.ecli is None
    assert decision.decision_date is None
    assert decision.summary is None
    assert decision.solution is None
    assert decision.text is None
    assert decision.update_date is None


# ---------------------------------------------------------------------------
# url fallback branches
# ---------------------------------------------------------------------------


def test_url_falls_back_to_id_when_file_entry_has_no_url_key():
    decision = JudilibreDecision(_full_decision(files=[{}], id="xyz789"))

    assert decision.url == "https://www.courdecassation.fr/decision/xyz789"


def test_url_is_none_when_no_files_and_no_id():
    decision = JudilibreDecision(_full_decision(files=[{}], id=""))

    assert decision.url is None


def test_url_prefers_first_file_link():
    decision = JudilibreDecision(
        _full_decision(files=[{"url": "https://example.com/doc.pdf"}, {"url": "other"}])
    )

    assert decision.url == "https://example.com/doc.pdf"


# ---------------------------------------------------------------------------
# to_markdown()
# ---------------------------------------------------------------------------


def test_to_markdown_includes_all_sections():
    decision = JudilibreDecision(_full_decision())

    markdown = decision.to_markdown()

    assert markdown.startswith("## Cour de cassation, Chambre sociale, 2020-03-04")
    assert "**Solution**: Rejet" in markdown
    assert "**ECLI**: ECLI:FR:CCASS:2020:SO00304" in markdown
    assert "**Référence**: abc123" in markdown
    assert "**URL**: https://www.courdecassation.fr/decision/abc123" in markdown
    assert "**Sommaire**: Résumé de la décision" in markdown
    assert "Texte intégral de la décision." in markdown


def test_to_markdown_uses_default_heading_when_no_jurisdiction_chamber_or_date():
    decision = JudilibreDecision(
        _full_decision(
            jurisdiction=None,
            chamber=None,
            decision_date=None,
            solution=None,
            ecli=None,
            summary=None,
            text=None,
            id="",
            files=[{}],
        )
    )

    markdown = decision.to_markdown()

    assert markdown.startswith("## Décision")
    # No solution/ecli/id/url/summary/text sections should be rendered.
    assert "**Solution**" not in markdown
    assert "**ECLI**" not in markdown
    assert "**Référence**" not in markdown
    assert "**URL**" not in markdown
    assert "**Sommaire**" not in markdown
