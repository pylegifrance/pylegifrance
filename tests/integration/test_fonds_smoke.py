"""Search test matrix — validates all search approaches an LLM might use.

Each test case validates:
- Results are non-empty
- First result has the expected article number (where applicable)
- Result has non-empty content
- Result has a valid URL
- Result has the correct code name (where applicable)
"""

from datetime import datetime

import pytest

from pylegifrance.fonds.code import Code
from pylegifrance.fonds.juri import JuriAPI
from pylegifrance.fonds.loda import Loda
from pylegifrance.models.code.enum import NomCode
from pylegifrance.models.loda.search import SearchRequest as LodaSearchRequest


@pytest.fixture(scope="module")
def code_api(api_client) -> Code:
    return Code(api_client)


@pytest.fixture(scope="module")
def loda_api(api_client) -> Loda:
    return Loda(api_client)


@pytest.fixture(scope="module")
def juri_api(api_client) -> JuriAPI:
    return JuriAPI(api_client)


# 1. Code: recherche par numero d'article


def test_code_search_by_article_number(code_api):
    results = code_api.search().in_code(NomCode.CC).article_number("1240").execute()

    assert len(results) > 0
    first = results[0]
    assert first.number == "1240"
    assert first.content or first.content_html
    assert first.url
    assert first.code_name


# 2. Code: recherche par numero d'article avec prefixe legislatif


def test_code_search_by_prefixed_article_number(code_api):
    results = code_api.search().in_code(NomCode.CDT).article_number("L1221-1").execute()

    assert len(results) > 0
    first = results[0]
    assert first.number == "L1221-1"
    assert first.content or first.content_html
    assert first.url


# 3. Code: recherche par mot-cle dans un code


def test_code_search_by_keyword(code_api):
    results = code_api.search().in_code(NomCode.CDT).text("periode d'essai").execute()

    assert len(results) > 0
    for article in results:
        assert article.id
        assert article.number


# 4. Code: recherche dans plusieurs codes


def test_code_search_multiple_codes(code_api):
    results = (
        code_api.search().in_codes([NomCode.CC, NomCode.CDT]).text("contrat").execute()
    )

    assert len(results) > 0
    for article in results:
        assert article.id


# 5. Code: recuperation par identifiant LEGIARTI


def test_code_fetch_by_legiarti_id(code_api):
    now = datetime.now().strftime("%Y-%m-%d")
    # LEGIARTI000032041571 = Article 1240 du Code civil (version post-reforme 2016)
    article = code_api.fetch_article("LEGIARTI000032041571").at(now)

    assert article is not None
    assert article.id
    assert article.number == "1240"
    assert article.content or article.content_html
    assert article.url
    assert article.code_name


# 6. LODA: recherche par mot-cle


def test_loda_search_by_keyword(loda_api):
    results = loda_api.search("teletravail")

    assert len(results) > 0
    first = results[0]
    assert first.id
    assert first.titre


# 7. LODA: recherche par nature LOI


def test_loda_search_by_nature(loda_api):
    search_request = LodaSearchRequest(
        search="travail",
        natures=["LOI"],
        page_size=5,
    )
    results = loda_api.search(search_request)

    assert len(results) > 0
    for texte in results:
        assert texte.id
        assert texte.titre
        assert "loi" in texte.titre.lower()


# 8. LODA: consultation par ID


def test_loda_fetch_by_id(loda_api):
    # LEGITEXT000006072050 = Code du travail
    texte = loda_api.fetch("LEGITEXT000006072050")

    assert texte is not None
    assert texte.id
    assert texte.titre
    assert texte.texte_html or texte.sections or texte.articles


# 9. Jurisprudence: recherche par mot-cle


def test_juri_search_by_keyword(juri_api):
    results = juri_api.search("requalification CDD")

    assert len(results) > 0
    first = results[0]
    assert first.id
    assert first.text or first.text_html


# 10. Jurisprudence: consultation par ID


def test_juri_fetch_by_id(juri_api):
    # First search to get a valid ID
    results = juri_api.search("contrat travail")
    assert len(results) > 0

    text_id = results[0].id
    assert text_id

    decision = juri_api.fetch(text_id)

    assert decision is not None
    assert decision.id == text_id
    assert decision.text or decision.text_html
    assert decision.title or decision.long_title
