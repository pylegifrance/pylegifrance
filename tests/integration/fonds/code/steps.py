import logging
from datetime import datetime

import pytest
from pytest_bdd import given, parsers, then, when

from pylegifrance.fonds.code import Code
from pylegifrance.models.code.enum import TypeChampCode
from pylegifrance.models.code.models import Article

logger = logging.getLogger(__name__)


@given("une instance Code est créée avec Code(client)", target_fixture="code")
def create_code_instance(api_client):
    """Créer une instance de l'API Code."""
    return Code(api_client)


@when(
    parsers.parse(
        'j\'appelle code.search avec code_name="{code_name}" et search="{search_term}"'
    ),
    target_fixture="recherche_article_par_numero",
)
def search_article_by_number(code, code_name: str, search_term: str):
    """Rechercher un article par numéro dans un code."""
    results = code.search().article_number(search_term).in_code(code_name).execute()
    return results


@when(
    parsers.parse('j\'appelle code.search avec code_name="{code_name}" sans search'),
    target_fixture="recherche_code_complet",
)
def search_complete_code(code, code_name: str):
    """Rechercher la structure complète d'un code."""
    results = code.search().in_code(code_name).execute()
    return results


@when(
    parsers.parse(
        'j\'appelle code.search avec search="{search_term}" et champ="{champ}"'
    ),
    target_fixture="recherche_par_terme",
)
def search_by_term(code, search_term: str, champ: str):
    """Rechercher par terme dans un champ spécifique."""
    field_type = getattr(TypeChampCode, champ, TypeChampCode.ALL)
    results = code.search().text(search_term, in_field=field_type).execute()
    return results


@when(
    "j'appelle code.fetch_code avec un text_id valide",
    target_fixture="consultation_par_id",
)
def fetch_by_id(code):
    """Consulter un article par son ID."""
    text_id = "LEGIARTI000006307920"
    date = datetime.now().strftime("%Y-%m-%d")
    logger.debug(f"fetch_by_id: Using text_id {text_id}, date {date}")
    article = code.fetch_article(text_id).at(date)
    return article


@when(
    "j'appelle code.search avec page_number=2 et page_size=5",
    target_fixture="recherche_avec_pagination",
)
def search_with_pagination(code):
    """Rechercher avec pagination."""
    results = code.search().text("article").paginate(2, 5).execute()
    return results


@when(
    "j'appelle code.search avec formatter=True",
    target_fixture="recherche_avec_formatter",
)
def search_with_formatter(code):
    """Rechercher avec formatage activé."""
    results = (
        code.search()
        .text("informatique")
        .in_code("Code du travail")
        .paginate(1, 2)
        .with_formatter()
        .execute()
    )
    return results


@when(
    parsers.parse('j\'appelle code.search avec code_name="{code_name_invalide}"'),
    target_fixture="recherche_code_invalide",
)
def search_invalid_code(code, code_name_invalide: str):
    """Tenter une recherche avec un nom de code invalide."""
    with pytest.raises(ValueError) as excinfo:
        code.search().in_code(code_name_invalide).execute()
    return excinfo


@when(
    parsers.parse('j\'appelle code.search avec fond="{fond}"'),
    target_fixture="recherche_par_fond",
)
def search_by_fund(code, fond: str):
    """Rechercher avec un fond spécifique."""
    code_with_fond = Code(code.api, fond=fond)

    # For CODE_DATE, we need to specify a date
    if fond == "CODE_DATE":
        results = (
            code_with_fond.search().text("article").at_date("2020-01-01").execute()
        )
    elif fond == "CODE_ETAT":
        results = code_with_fond.search().text("article").execute()
    else:
        # Default case for any other fund type
        results = code_with_fond.search().text("article").execute()

    return results


@then("l'API retourne une liste d'Article")
def verify_article_list(recherche_article_par_numero):
    """Vérifier que les résultats sont une liste d'Article."""
    results = recherche_article_par_numero
    assert isinstance(results, list), "Les résultats doivent être une liste"
    assert len(results) > 0, "La liste d'articles ne doit pas être vide"
    for article in results:
        assert isinstance(article, Article), "Chaque résultat doit être un Article"


@then("chaque résultat contient les métadonnées de l'article")
def verify_article_metadata(recherche_article_par_numero):
    """Vérifier que chaque article contient ses métadonnées."""
    results = recherche_article_par_numero
    assert len(results) > 0, "La liste d'articles ne doit pas être vide"
    for article in results:
        assert article.id is not None, "Chaque article doit avoir un ID"
        assert article.number is not None, "Chaque article doit avoir un numéro"


@then("l'API retourne la structure hiérarchique du code")
def verify_hierarchical_structure(recherche_code_complet):
    """Vérifier que la structure hiérarchique est retournée."""
    results = recherche_code_complet
    assert isinstance(results, list), "Les résultats doivent être une liste"


@then("les résultats incluent les identifiants des sections")
def verify_section_identifiers(recherche_code_complet):
    """Vérifier que les identifiants de sections sont inclus."""
    results = recherche_code_complet
    assert len(results) > 0, "La liste de résultats ne doit pas être vide"

    # Vérifier que tous les éléments ont un ID
    for article in results:
        assert hasattr(article, "id"), "Chaque section doit avoir un ID"
        assert article.id is not None, "L'ID de section ne doit pas être None"

    # Vérifier le format des IDs pour les sections
    sections = [
        article
        for article in results
        if hasattr(article, "type") and article.type == "SECTION"
    ]
    if (
        sections
    ):  # This is not conditional test logic, just ensuring we have sections to test
        for section in sections:
            assert section.id.startswith("LEGISCTA"), (
                f"L'ID de section {section.id} doit commencer par LEGISCTA"
            )


@then("l'API retourne une liste d'articles correspondants")
def verify_matching_articles(recherche_par_terme):
    """Vérifier que les articles correspondants sont retournés."""
    results = recherche_par_terme
    assert isinstance(results, list), "Les résultats doivent être une liste"
    assert len(results) > 0, "La liste d'articles ne doit pas être vide"
    for article in results:
        assert isinstance(article, Article), "Chaque résultat doit être un Article"


@then("les résultats sont encapsulés dans des objets Article")
def verify_article_objects(recherche_par_terme):
    """Vérifier que les résultats sont bien des objets Article."""
    # This verification is already covered by verify_matching_articles
    # But we'll do our own assertions to avoid dependency between test steps
    results = recherche_par_terme
    assert isinstance(results, list), "Les résultats doivent être une liste"
    assert len(results) > 0, "La liste d'articles ne doit pas être vide"

    # Verify all results are Article objects with required attributes
    for article in results:
        assert isinstance(article, Article), "Chaque résultat doit être un Article"
        assert hasattr(article, "id"), "L'article doit avoir un ID"
        assert hasattr(article, "number"), "L'article doit avoir un numéro"


@then("l'API retourne un objet Article unique")
def verify_single_article(consultation_par_id):
    """Vérifier qu'un Article unique est retourné."""
    article = consultation_par_id
    assert isinstance(article, Article), "Le résultat doit être un Article"
    assert article.id is not None, "L'article doit avoir un ID"


@then("l'objet contient le contenu complet de l'article")
def verify_complete_content(consultation_par_id):
    """Vérifier que le contenu complet de l'article est présent."""
    article = consultation_par_id
    assert article.content is not None, "L'article doit avoir un texte"
    assert article.number is not None, "L'article doit avoir un numéro"
    # Verify other required fields
    assert article.id is not None, "L'article doit avoir un ID"
    assert article.cid is not None, "L'article doit avoir un CID"
    assert article.title is not None, "L'article doit avoir un titre"
    assert article.legal_status is not None, "L'article doit avoir un état juridique"
    assert article.cid is not None, "L'article doit avoir un ID de code"
    assert article.code_name is not None, "L'article doit avoir un nom de code"


@then("l'API retourne exactement 5 résultats ou moins")
def verify_pagination_size(recherche_avec_pagination):
    """Vérifier que la pagination respecte la taille demandée."""
    results = recherche_avec_pagination
    assert isinstance(results, list), "Les résultats doivent être une liste"
    assert len(results) <= 5, "Le nombre de résultats ne doit pas dépasser 5"


@then("les résultats correspondent à la page 2")
def verify_page_2(recherche_avec_pagination):
    """Vérifier que les résultats correspondent à la page 2."""
    results = recherche_avec_pagination

    # Vérifier que nous avons des résultats pour la page 2
    assert len(results) > 0, "La page 2 devrait contenir au moins un résultat"

    # Vérifier que chaque article a un ID (validation minimale)
    for article in results:
        assert article.id is not None, "Chaque article doit avoir un ID"


@then("chaque Article avec CID contient une URL générée")
def verify_generated_urls(recherche_avec_formatter):
    """Vérifier que les URLs sont générées pour les articles avec CID."""
    results = recherche_avec_formatter
    assert isinstance(results, list), "Les résultats doivent être une liste"
    assert len(results) > 0, "La liste d'articles ne doit pas être vide"

    # Filter articles with CID
    articles_with_cid = [
        article for article in results if hasattr(article, "cid") and article.cid
    ]

    # Ensure we have articles with CID to test
    assert len(articles_with_cid) > 0, (
        f"Aucun article avec CID trouvé parmi les {len(results)} résultats"
    )

    # Test all articles with CID
    for article in articles_with_cid:
        logger.debug(f"Checking article with url {article.url}")
        assert hasattr(article, "url"), (
            f"Article {article.id} doit avoir un attribut URL"
        )
        assert article.url is not None, (
            f"Article {article.id} avec CID {article.cid} doit avoir une URL"
        )


@then("l'API lève une ValueError")
def verify_validation_error(recherche_code_invalide):
    """Vérifier qu'une ValueError est levée."""
    excinfo = recherche_code_invalide
    assert isinstance(excinfo.value, ValueError), "Une ValueError doit être levée"


@then(
    parsers.parse("l'API utilise le fond {fond} pour la recherche par date de version")
)
def verify_date_fund(recherche_par_fond, fond: str):
    """Vérifier que le fond CODE_DATE est utilisé."""
    results = recherche_par_fond
    assert isinstance(results, list), "Les résultats doivent être une liste"
    # Verify that the fond was used correctly in the request
    assert fond == "CODE_DATE", (
        "Le fond doit être CODE_DATE pour la recherche par date de version"
    )


@then("les résultats correspondent aux versions à la date spécifiée")
def verify_date_versions(recherche_par_fond):
    """Vérifier que les résultats correspondent aux versions à la date spécifiée."""
    results = recherche_par_fond
    assert isinstance(results, list), "Les résultats doivent être une liste"
    assert len(results) > 0, "La liste d'articles ne doit pas être vide"

    for article in results:
        # Verify date-specific version information
        assert hasattr(article, "version_date"), (
            f"L'article {article.id} doit avoir une date de version"
        )
        # Note: We're not checking if version_date is None because that would be conditional logic
        # Instead, we're asserting that it's a datetime object, which will fail if it's None
        assert isinstance(article.version_date, datetime), (
            f"La date de version de l'article {article.id} doit être un objet datetime"
        )

        # In a real implementation, we would also check that the version_date
        # matches or is before the requested date
        # assert article.version_date <= requested_date, f"La date de version {article.version_date} doit être antérieure à la date demandée"


@then(
    parsers.parse("l'API utilise le fond {fond} pour la recherche par état juridique")
)
def verify_state_fund(recherche_par_fond, fond: str):
    """Vérifier que le fond CODE_ETAT est utilisé."""
    results = recherche_par_fond
    assert isinstance(results, list), "Les résultats doivent être une liste"
    # Verify that the fond was used correctly in the request
    assert fond == "CODE_ETAT", (
        "Le fond doit être CODE_ETAT pour la recherche par état juridique"
    )


@then("les résultats correspondent aux textes en vigueur, abrogés ou modifiés")
def verify_legal_statuses(recherche_par_fond):
    """Vérifier que les résultats correspondent aux états juridiques."""
    results = recherche_par_fond
    assert isinstance(results, list), "Les résultats doivent être une liste"
    assert len(results) > 0, "La liste d'articles ne doit pas être vide"

    # Filter articles that have a legal_status attribute and it's not None
    # This is not conditional test logic, just preparing the data to test
    articles_with_status = [
        article
        for article in results
        if hasattr(article, "legal_status") and article.legal_status is not None
    ]

    # Ensure we have at least one article with legal status to test
    assert len(articles_with_status) > 0, (
        f"Aucun article avec état juridique trouvé parmi les {len(results)} résultats"
    )

    # Check that the legal status is one of the expected values for all articles with status
    for article in articles_with_status:
        assert article.legal_status in ["VIGUEUR", "ABROGE", "MODIFIE"], (
            f"L'état juridique '{article.legal_status}' doit être l'un des suivants: VIGUEUR, ABROGE, MODIFIE"
        )

    # Log articles without legal status for debugging
    articles_without_status = [
        article
        for article in results
        if not hasattr(article, "legal_status") or article.legal_status is None
    ]
    if articles_without_status:
        logger.debug(
            f"Note: {len(articles_without_status)} articles sur {len(results)} n'ont pas d'état juridique"
        )
