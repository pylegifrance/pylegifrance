"""Contract tests: assert the public API surface matches what the docs claim."""

import inspect

from pylegifrance.client import LegifranceClient
from pylegifrance.fonds.code import CodeSearchBuilder
from pylegifrance.fonds.juri import JuriAPI, JuriDecision
from pylegifrance.fonds.loda import TexteLoda
from pylegifrance.models.code.enum import TypeChampCode
from pylegifrance.models.constants import EtatJuridique


def test_typechampcode_has_article_not_text():
    assert hasattr(TypeChampCode, "ARTICLE")
    assert not hasattr(TypeChampCode, "TEXT")


def test_etatjuridique_correct_names():
    for name in ("VIGUEUR", "VIGUEUR_DIFF", "ABROGE", "ABROGE_DIFF", "MODIFIE"):
        assert hasattr(EtatJuridique, name), f"EtatJuridique.{name} missing"
    assert not hasattr(EtatJuridique, "VIGUEUR_AVEC_TERME")
    assert not hasattr(EtatJuridique, "VIGUEUR_DIFFEREE")


def test_update_api_keys_param_names():
    sig = inspect.signature(LegifranceClient.update_api_keys)
    params = list(sig.parameters)
    assert "client_id" in params
    assert "client_secret" in params
    assert "legifrance_api_key" not in params


def test_with_legal_status_default_is_none():
    sig = inspect.signature(CodeSearchBuilder.with_legal_status)
    assert sig.parameters["status"].default is None


def test_juriapi_v132_methods():
    for method in ("fetch_by_id", "search_by_ecli", "search_by_affaire"):
        assert hasattr(JuriAPI, method), f"JuriAPI.{method} missing"


def test_texteloda_texte_brut():
    assert hasattr(TexteLoda, "texte_brut"), "TexteLoda.texte_brut missing"


def test_juridecision_url():
    assert hasattr(JuriDecision, "url"), "JuriDecision.url missing"
