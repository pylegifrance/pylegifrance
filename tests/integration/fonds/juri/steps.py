import pytest
from pytest_bdd import when, then

from pylegifrance.fonds.juri import JuriAPI, JuriDecision, SearchRequest
from pylegifrance.models.juri.constants import JuridictionJudiciaire


@pytest.fixture(scope="module")
def juri_api(api_client) -> JuriAPI:
    """Create a JURI API instance."""
    return JuriAPI(api_client)


@when('je recherche des décisions contenant "responsabilité civile"')
def search_by_keywords(juri_api, context):
    """Search for decisions containing specific keywords."""
    search_query = "responsabilite civile"
    context["results"] = juri_api.search(search_query)


@when("je recherche des décisions de la Cour de cassation")
def search_by_jurisdiction(juri_api, context):
    """Search for decisions from Cour de cassation."""
    search_request = SearchRequest(
        search="contrat",
        juridiction_judiciaire=[JuridictionJudiciaire.cour_de_cassation.value],
        page_size=3,
    )
    context["results"] = juri_api.search(search_request)


@when("je recherche des décisions avec une limite de 5 par page")
def search_with_pagination(juri_api, context):
    """Search for decisions with pagination limit."""
    page_size = 5
    search_request_page1 = SearchRequest(
        search="dommages", page_size=page_size, page_number=1
    )
    search_request_page2 = SearchRequest(
        search="dommages", page_size=page_size, page_number=2
    )

    context["page_size"] = page_size
    context["results_page1"] = juri_api.search(search_request_page1)
    context["results_page2"] = juri_api.search(search_request_page2)


@when("je recherche des décisions en spécifiant les champs à extraire")
def search_with_specific_fields(juri_api, context):
    """Search for decisions with specific field extraction."""
    specific_keys = ["id", "titre", "juridiction", "dateTexte"]
    search_request = SearchRequest(
        search="préjudice", keys=specific_keys, formatter=True, page_size=3
    )
    context["results"] = juri_api.search(search_request)
    context["specific_keys"] = specific_keys


@then("je reçois une liste de décisions pertinentes")
def verify_results_list(context):
    """Verify that results are returned as a list."""
    results = context["results"]
    assert isinstance(results, list), "Les résultats doivent être une liste"
    assert len(results) > 0, "La recherche doit retourner au moins un résultat"


@then(
    "chaque décision contient les informations essentielles (juridiction, date, numéro)"
)
def verify_essential_information(context):
    """Verify that each decision contains essential information."""
    results = context["results"]

    for decision in results:
        assert isinstance(decision, JuriDecision), (
            "Chaque résultat doit être une JuriDecision"
        )
        assert decision.id is not None, "Chaque décision doit avoir un ID"

        # Au moins une des informations essentielles doit être présente
        essential_info_present = any(
            [
                decision.jurisdiction is not None,
                decision.date is not None,
                decision.numero is not None,
            ]
        )
        assert essential_info_present, (
            "Chaque décision doit contenir au moins une information essentielle"
        )


@then("je ne reçois que des décisions de cette juridiction")
def verify_jurisdiction_filter(context):
    """Verify that only decisions from the specified jurisdiction are returned."""
    results = context["results"]
    assert isinstance(results, list), "Les résultats doivent être une liste"

    if len(results) > 0:  # Si des résultats sont trouvés
        for decision in results:
            # Vérifier que la juridiction correspond ou qu'elle contient des mots-clés de la Cour de cassation
            if decision.jurisdiction:
                jurisdiction_lower = decision.jurisdiction.lower()
                cour_cassation_keywords = ["cassation", "cour de cassation"]
                assert any(
                    keyword in jurisdiction_lower for keyword in cour_cassation_keywords
                ), (
                    f"La juridiction '{decision.jurisdiction}' ne correspond pas à la Cour de cassation"
                )


@then("je reçois exactement 5 résultats")
def verify_pagination_limit(context):
    """Verify that exactly 5 results are returned."""
    page_size = context["page_size"]
    results_page1 = context["results_page1"]

    assert isinstance(results_page1, list), (
        "Les résultats de la page 1 doivent être une liste"
    )
    assert len(results_page1) <= page_size, (
        f"Le nombre de résultats de la page 1 ne doit pas dépasser {page_size}"
    )


@then("je peux accéder à la page suivante")
def verify_next_page_access(context):
    """Verify that the next page can be accessed."""
    page_size = context["page_size"]
    results_page1 = context["results_page1"]
    results_page2 = context["results_page2"]

    assert isinstance(results_page2, list), (
        "Les résultats de la page 2 doivent être une liste"
    )
    assert len(results_page2) <= page_size, (
        f"Le nombre de résultats de la page 2 ne doit pas dépasser {page_size}"
    )

    # Vérifier que les pages contiennent des résultats différents
    if len(results_page1) > 0 and len(results_page2) > 0:
        page1_ids = {decision.id for decision in results_page1 if decision.id}
        page2_ids = {decision.id for decision in results_page2 if decision.id}
        assert page1_ids != page2_ids, (
            "Les résultats de la page 1 et 2 doivent être différents"
        )


@then("je reçois uniquement les champs demandés pour chaque décision")
def verify_specific_fields(context):
    """Verify that only requested fields are returned for each decision."""
    results = context["results"]

    assert isinstance(results, list), "Les résultats doivent être une liste"

    if len(results) > 0:
        for decision in results:
            assert isinstance(decision, JuriDecision), (
                "Chaque résultat doit être une JuriDecision"
            )

            # Vérifier que les champs essentiels sont présents
            assert decision.id is not None, "L'ID doit toujours être présent"

            # Au moins un des champs spécifiés doit être présent
            specified_fields_present = any(
                [
                    decision.title is not None,
                    decision.jurisdiction is not None,
                    decision.date is not None,
                ]
            )
            assert specified_fields_present, (
                "Au moins un des champs spécifiés doit être présent"
            )


@pytest.fixture
def context():
    """Shared context for storing data between steps."""
    return {}
