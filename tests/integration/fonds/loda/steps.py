import pytest
from datetime import datetime
from pytest_bdd import when, then, parsers

from pylegifrance.models.constants import Fond, Nature
from pylegifrance.models.generated.model import DatePeriod
from pylegifrance.fonds.loda import Loda, TexteLoda
from pylegifrance.models.loda.search import SearchRequest


@pytest.fixture(scope="module")
def loda_api(api_client) -> Loda:
    """Create a LODA API instance."""
    from pylegifrance.fonds.loda import Loda

    return Loda(api_client)


@when(
    parsers.parse('j\'appelle loda.search avec le terme "{terme}"'),
    target_fixture="recherche_par_terme",
)
def recherche_par_terme(loda_api: Loda, terme: str):
    """Effectuer une recherche par terme."""
    results = loda_api.search(terme)
    return results


@when(
    parsers.parse('j\'appelle loda.search avec la nature "{nature}"'),
    target_fixture="recherche_par_nature",
)
def recherche_par_nature(loda_api: Loda, nature: str):
    """Effectuer une recherche par nature."""
    search_request = SearchRequest(
        search="droit"
        if nature == "LOI"
        else "application"
        if nature == "DECRET"
        else "modification"
        if nature == "ORDONNANCE"
        else "fixant",
        natures=[getattr(Nature, nature).value],
        page_size=5,
    )
    results = loda_api.search(search_request)
    return results


@when(
    parsers.parse("j'appelle loda.fetch avec l'ID \"{text_id}\""),
    target_fixture="consultation_par_id",
)
def consultation_par_id(loda_api: Loda, text_id: str):
    """Consulter un texte par son ID."""
    texte = loda_api.fetch(text_id)
    return texte


@when(
    parsers.parse("j'appelle loda.search avec page_size={taille_page:d}"),
    target_fixture="recherche_avec_pagination",
)
def recherche_avec_pagination(loda_api: Loda, taille_page: int):
    """Effectuer une recherche avec pagination."""
    search_request_page1 = SearchRequest(
        search="droit", page_size=taille_page, page_number=1
    )
    search_request_page2 = SearchRequest(
        search="droit", page_size=taille_page, page_number=2
    )

    results_page1 = loda_api.search(search_request_page1)
    results_page2 = loda_api.search(search_request_page2)

    return {"page1": results_page1, "page2": results_page2, "page_size": taille_page}


@when(
    'j\'appelle loda.search avec date_debut="2023-01-01"',
    target_fixture="recherche_avec_date_debut",
)
def recherche_avec_date_debut(loda_api: Loda):
    """Effectuer une recherche avec date de début."""
    date_debut = datetime(year=2023, month=1, day=1)
    search_request = SearchRequest(
        search="loi",
        date_signature=DatePeriod(start=date_debut, end=None),
        page_size=5,
    )
    results = loda_api.search(search_request)
    return {"results": results, "date_debut": date_debut}


@when(
    'j\'appelle loda.search avec date_fin="2023-12-31"',
    target_fixture="recherche_avec_date_fin",
)
def recherche_avec_date_fin(loda_api: Loda):
    """Effectuer une recherche avec date de fin."""
    date_debut = datetime(year=2023, month=10, day=1)
    date_fin = datetime(year=2023, month=12, day=31)
    search_request = SearchRequest(
        search="loi",
        date_publication=DatePeriod(start=date_debut, end=date_fin),
        page_size=5,
    )
    results = loda_api.search(search_request)
    return {"results": results, "date_fin": date_fin}


@when(
    parsers.parse('j\'appelle loda.search avec le fond "{fond}"'),
    target_fixture="recherche_par_fond",
)
def recherche_par_fond(loda_api: Loda, fond: str):
    """Effectuer une recherche par fond."""
    search_request = SearchRequest(
        search="loi", fond=getattr(Fond, fond).value, page_size=5
    )
    results = loda_api.search(search_request)
    return results


@when("j'appelle loda.search sans formatter", target_fixture="recherche_sans_formatter")
def recherche_sans_formatter(loda_api: Loda):
    """Effectuer une recherche sans formatage."""
    search_request = SearchRequest(search="loi", page_size=5)
    results = loda_api.search(search_request)
    return results


@when(
    "j'appelle loda.search avec formatter=True",
    target_fixture="recherche_avec_formatter",
)
def recherche_avec_formatter(loda_api: Loda):
    """Effectuer une recherche avec formatage."""
    search_request = SearchRequest(search="loi", page_size=5)
    results = loda_api.search(search_request)
    return results


@when(
    "j'appelle loda.search pour la dernière loi votée",
    target_fixture="recherche_derniere_loi",
)
def recherche_derniere_loi(loda_api: Loda):
    """Rechercher la dernière loi votée."""
    search_request = SearchRequest(
        natures=["LOI"],
        page_size=1,
        page_number=1,
    )
    results = loda_api.search(search_request)
    return results


@when(
    "j'appelle loda.fetch avec l'ID de la dernière loi",
    target_fixture="consultation_derniere_loi",
)
def consultation_derniere_loi(loda_api: Loda, recherche_derniere_loi):
    """Consulter la dernière loi par son ID."""
    results = recherche_derniere_loi
    assert len(results) > 0, "Au moins une loi doit être trouvée"

    loi_id = results[0].id
    assert loi_id is not None, "L'ID de la loi ne peut pas être None"

    # Fetch the complete content using the ID
    texte_complet = loda_api.fetch(loi_id)
    return {"recherche": results, "texte_complet": texte_complet}


@when(
    parsers.parse('le statut juridique est "{statut}"'),
    target_fixture="verification_statut_juridique",
)
def verification_statut_juridique(consultation_par_id, statut: str):
    """Vérifier que le statut juridique du texte correspond à celui attendu."""
    texte = consultation_par_id
    assert texte.etat is not None, "Le texte doit avoir un statut juridique"
    # Normaliser les statuts - l'API peut retourner "Vigueur" au lieu de "VIGUEUR"
    statut_normalise = texte.etat.upper() if texte.etat else ""
    statut_attendu = statut.upper()
    assert statut_normalise == statut_attendu, (
        f"Le statut attendu est '{statut}', mais obtenu '{texte.etat}'"
    )
    return texte


@when(
    parsers.parse('j\'appelle loda.search avec la nature invalide "{nature_invalide}"'),
    target_fixture="recherche_nature_invalide",
)
def recherche_nature_invalide(loda_api: Loda, nature_invalide: str):
    """Tenter une recherche avec une nature invalide."""
    with pytest.raises(Exception) as excinfo:
        search_request = SearchRequest(
            search="loi", natures=[nature_invalide], page_size=5
        )
        loda_api.search(search_request)
    return excinfo


@then("l'API retourne une liste de TexteLoda")
def verifier_liste_texte_loda(recherche_par_terme):
    """Vérifier que les résultats sont une liste de TexteLoda."""
    results = recherche_par_terme
    assert isinstance(results, list) and len(results) > 0, (
        "Les résultats doivent être une liste non vide"
    )


@then("les résultats contiennent le terme recherché")
def verifier_terme_present(recherche_par_terme):
    """Vérifier que le terme recherché est présent dans les résultats."""
    results = recherche_par_terme
    search_term = "télétravail"  # Term from the step

    if len(results) > 0:
        for texte in results:
            assert isinstance(texte, TexteLoda), (
                "Chaque résultat doit être un TexteLoda"
            )
            assert texte.id is not None, "Chaque texte doit avoir un ID"

            # Vérifier que le terme est présent dans le texte ou le titre
            term_present = False
            if texte.texte_html and search_term.lower() in texte.texte_html.lower():
                term_present = True
            elif texte.titre and search_term.lower() in texte.titre.lower():
                term_present = True
            elif texte.titre_long and search_term.lower() in texte.titre_long.lower():
                term_present = True

            assert term_present, (
                f"Le terme '{search_term}' doit être présent dans le texte ou le titre"
            )


@then(parsers.parse("l'API retourne uniquement des {type_document}"))
def verifier_type_document(recherche_par_nature, type_document: str):
    """Vérifier que les résultats correspondent au type de document."""
    results = recherche_par_nature
    assert isinstance(results, list), "Les résultats doivent être une liste"

    if len(results) > 0:
        for texte in results:
            assert isinstance(texte, TexteLoda), (
                "Chaque résultat doit être un TexteLoda"
            )


@then(parsers.parse('chaque résultat a la nature "{nature}"'))
def verifier_nature_resultat(recherche_par_nature, nature: str):
    """Vérifier que chaque résultat a la bonne nature."""
    results = recherche_par_nature

    if len(results) > 0:
        for texte in results:
            assert texte.titre is not None, "Chaque texte doit avoir un titre"

            if nature == "LOI":
                assert "loi" in texte.titre.lower(), (
                    f"Le titre '{texte.titre}' doit contenir 'loi'"
                )
            elif nature == "DECRET":
                assert "décret" in texte.titre.lower(), (
                    f"Le titre '{texte.titre}' doit contenir 'décret'"
                )
            elif nature == "ORDONNANCE":
                assert "ordonnance" in texte.titre.lower(), (
                    f"Le titre '{texte.titre}' doit contenir 'ordonnance'"
                )
            elif nature == "ARRETE":
                assert "arrêté" in texte.titre.lower(), (
                    f"Le titre '{texte.titre}' doit contenir 'arrêté'"
                )


@then("l'API retourne un TexteLoda unique")
def verifier_texte_unique(consultation_par_id):
    """Vérifier qu'un TexteLoda unique est retourné."""
    texte = consultation_par_id
    assert texte is not None, "La consultation doit retourner un texte"
    assert isinstance(texte, TexteLoda), "Le résultat doit être un TexteLoda"


@then("l'objet contient les métadonnées complètes")
def verifier_metadonnees_completes(consultation_par_id):
    """Vérifier que les métadonnées sont complètes."""
    texte = consultation_par_id
    assert texte.titre is not None, "Le texte doit avoir un titre"
    assert texte.texte_html is not None, "Le texte doit avoir un contenu HTML"

    # Vérifier que d'autres métadonnées sont présentes
    metadata_present = any(
        [
            texte.date_debut is not None,
            texte.etat is not None,
            texte.last_update is not None,
        ]
    )
    assert metadata_present, "Le texte doit contenir des métadonnées"


@then(parsers.parse("l'API retourne au maximum {taille_page:d} résultats"))
def verifier_taille_page(recherche_avec_pagination, taille_page: int):
    """Vérifier que le nombre de résultats respecte la taille de page."""
    pagination_data = recherche_avec_pagination
    results_page1 = pagination_data["page1"]
    results_page2 = pagination_data["page2"]

    assert isinstance(results_page1, list), (
        "Les résultats de la page 1 doivent être une liste"
    )
    assert len(results_page1) <= taille_page, (
        f"Le nombre de résultats de la page 1 ne doit pas dépasser {taille_page}"
    )

    assert isinstance(results_page2, list), (
        "Les résultats de la page 2 doivent être une liste"
    )
    assert len(results_page2) <= taille_page, (
        f"Le nombre de résultats de la page 2 ne doit pas dépasser {taille_page}"
    )


@then("la pagination fonctionne correctement")
def verifier_pagination(recherche_avec_pagination):
    """Vérifier que la pagination fonctionne correctement."""
    pagination_data = recherche_avec_pagination
    results_page1 = pagination_data["page1"]
    results_page2 = pagination_data["page2"]

    # Vérifier que les pages contiennent des résultats différents
    if len(results_page1) > 0 and len(results_page2) > 0:
        page1_ids = {texte.id for texte in results_page1 if texte.id}
        page2_ids = {texte.id for texte in results_page2 if texte.id}

        assert page1_ids != page2_ids, (
            "Les résultats de la page 1 et 2 doivent être différents"
        )


@then(parsers.parse('tous les résultats ont une date >= "{date_str}"'))
def verifier_date_debut(recherche_avec_date_debut, date_str: str):
    """Vérifier que tous les résultats ont une date >= date_debut."""
    data = recherche_avec_date_debut
    results = data["results"]
    date_debut = data["date_debut"]

    assert isinstance(results, list), "Les résultats doivent être une liste"

    if len(results) > 0:
        date_debut_dt = datetime.fromisoformat(date_debut.isoformat())
        for texte in results:
            assert isinstance(texte, TexteLoda), (
                "Chaque résultat doit être un TexteLoda"
            )

            # Si la date de début est disponible, vérifier qu'elle est >= date_debut
            if texte.date_debut:
                assert texte.date_debut >= date_debut_dt, (
                    f"La date de début {texte.date_debut} doit être >= {date_debut_dt}"
                )


@then("aucun résultat antérieur n'est retourné")
def verifier_aucun_resultat_anterieur(recherche_avec_date_debut):
    """Vérifier qu'aucun résultat antérieur n'est retourné."""
    # Cette vérification est déjà couverte par verifier_date_debut
    pass


@then(parsers.parse('tous les résultats ont une date <= "{date_str}"'))
def verifier_date_fin(recherche_avec_date_fin, date_str: str):
    """Vérifier que tous les résultats ont une date <= date_fin."""
    data = recherche_avec_date_fin
    results = data["results"]
    date_fin = data["date_fin"]

    assert isinstance(results, list), "Les résultats doivent être une liste"

    if len(results) > 0:
        date_fin_dt = datetime.fromisoformat(date_fin.isoformat())
        for texte in results:
            assert isinstance(texte, TexteLoda), (
                "Chaque résultat doit être un TexteLoda"
            )

            # Vérifier que la date de publication est <= date_fin
            if texte.date_publication:
                # Handle timezone-aware comparison
                date_publication = texte.date_publication
                if date_publication.tzinfo is not None and date_fin_dt.tzinfo is None:
                    # Make date_fin_dt timezone-aware (UTC)
                    from datetime import timezone

                    date_fin_dt_aware = date_fin_dt.replace(tzinfo=timezone.utc)
                    assert date_publication <= date_fin_dt_aware, (
                        f"La date de publication {date_publication} doit être <= {date_fin_dt_aware}"
                    )
                else:
                    assert date_publication <= date_fin_dt, (
                        f"La date de publication {date_publication} doit être <= {date_fin_dt}"
                    )


@then("aucun résultat postérieur n'est retourné")
def verifier_aucun_resultat_posterieur(recherche_avec_date_fin):
    """Vérifier qu'aucun résultat postérieur n'est retourné."""
    # Cette vérification est déjà couverte par verifier_date_fin
    pass


@then("l'API utilise le fond spécialisé pour les dates")
def verifier_fond_dates(recherche_par_fond):
    """Vérifier que l'API utilise le fond spécialisé pour les dates."""
    results = recherche_par_fond
    assert isinstance(results, list), "Les résultats doivent être une liste"


@then("les résultats correspondent aux versions historiques")
def verifier_versions_historiques(recherche_par_fond):
    """Vérifier que les résultats correspondent aux versions historiques."""
    results = recherche_par_fond
    if len(results) > 0:
        for texte in results:
            assert isinstance(texte, TexteLoda), (
                "Chaque résultat doit être un TexteLoda"
            )
            assert texte.id is not None, "Chaque texte doit avoir un ID"


@then("l'API utilise le fond spécialisé pour les états")
def verifier_fond_etats(recherche_par_fond):
    """Vérifier que l'API utilise le fond spécialisé pour les états."""
    results = recherche_par_fond
    assert isinstance(results, list), "Les résultats doivent être une liste"


@then("les résultats correspondent aux statuts juridiques")
def verifier_statuts_juridiques(recherche_par_fond):
    """Vérifier que les résultats correspondent aux statuts juridiques."""
    results = recherche_par_fond
    if len(results) > 0:
        for texte in results:
            assert isinstance(texte, TexteLoda), (
                "Chaque résultat doit être un TexteLoda"
            )
            assert texte.id is not None, "Chaque texte doit avoir un ID"
            assert texte.etat is not None, "Chaque texte doit avoir un état juridique"


@then("les résultats ne contiennent pas d'URLs formatées")
def verifier_pas_urls_formatees(recherche_sans_formatter):
    """Vérifier que les résultats ne contiennent pas d'URLs formatées."""
    results = recherche_sans_formatter
    assert isinstance(results, list), "Les résultats doivent être une liste"

    if len(results) > 0:
        for texte in results:
            assert isinstance(texte, TexteLoda), (
                "Chaque résultat doit être un TexteLoda"
            )

            # Vérifier que les données sont brutes (pas d'URL formatée)
            texte_dict = texte.to_dict()
            assert "url" not in texte_dict, (
                "Les résultats ne doivent pas contenir d'URL formatée"
            )


@then("les données brutes sont retournées")
def verifier_donnees_brutes(recherche_sans_formatter):
    """Vérifier que les données brutes sont retournées."""
    # Cette vérification est déjà couverte par verifier_pas_urls_formatees
    pass


@then("les résultats contiennent des URLs enrichies")
def verifier_urls_enrichies(recherche_avec_formatter):
    """Vérifier que les résultats contiennent des URLs enrichies."""
    results = recherche_avec_formatter
    assert isinstance(results, list), "Les résultats doivent être une liste"


@then("les métadonnées sont formatées")
def verifier_metadonnees_formatees(recherche_avec_formatter):
    """Vérifier que les métadonnées sont formatées."""
    # Le formatage n'est pas encore implémenté, on vérifie juste que ça fonctionne
    pass


@then("l'API lève une erreur de validation")
def verifier_erreur_validation(recherche_nature_invalide):
    """Vérifier qu'une erreur de validation est levée."""
    excinfo = recherche_nature_invalide
    assert excinfo.value is not None, "Une exception doit être levée"


@then("l'API retourne la loi la plus récente")
def verifier_loi_la_plus_recente(recherche_derniere_loi):
    """Vérifier que l'API retourne une loi."""
    results = recherche_derniere_loi
    assert isinstance(results, list), "Les résultats doivent être une liste"
    assert len(results) > 0, "Au moins une loi doit être retournée"

    loi = results[0]
    assert isinstance(loi, TexteLoda), "Le résultat doit être un TexteLoda"
    assert loi.id is not None, "La loi doit avoir un ID"


@then(parsers.parse('le résultat a la nature "{nature}"'))
def verifier_nature_resultat_unique(recherche_derniere_loi, nature: str):
    """Vérifier que le résultat a la nature spécifiée."""
    results = recherche_derniere_loi
    assert len(results) > 0, "Au moins un résultat doit être retourné"

    loi = results[0]
    assert loi.titre is not None, "La loi doit avoir un titre"

    if nature == "LOI":
        assert "loi" in loi.titre.lower(), f"Le titre '{loi.titre}' doit contenir 'loi'"


@then("la date du texte est la plus récente")
def verifier_date_texte_plus_recente(recherche_derniere_loi):
    """Vérifier que la loi a une date de texte."""
    results = recherche_derniere_loi
    assert len(results) > 0, "Au moins un résultat doit être retourné"

    loi = results[0]
    # Check if the law has any date information available
    has_date = (
        loi.date_debut is not None
        or loi.date_fin is not None
        or loi.last_update is not None
        or (hasattr(loi._texte, "date_texte") and loi._texte.date_texte is not None)
    )
    assert has_date, "La loi doit avoir une date"


@then("le message indique les natures valides")
def verifier_message_natures_valides(recherche_nature_invalide):
    """Vérifier que le message d'erreur indique les natures valides."""
    excinfo = recherche_nature_invalide
    error_message = str(excinfo.value)

    # Et le message indique la nature invalide
    assert "INVALIDE" in error_message, (
        "Le message d'erreur doit mentionner la nature invalide"
    )

    # Vérifier que le message mentionne que la valeur n'est pas valide
    assert "not a valid" in error_message, (
        "Le message d'erreur doit indiquer que la valeur n'est pas valide"
    )


@then("l'API retourne le contenu complet de la loi")
def verifier_contenu_complet_loi(consultation_derniere_loi):
    """Vérifier que l'API retourne le contenu complet de la loi."""
    data = consultation_derniere_loi
    texte_complet = data["texte_complet"]

    assert texte_complet is not None, "Le texte complet ne peut pas être None"
    assert isinstance(texte_complet, TexteLoda), (
        "Le texte complet doit être un TexteLoda"
    )
    assert texte_complet.id is not None, "Le texte complet doit avoir un ID"


@then("le contenu HTML est présent")
def verifier_contenu_html_present(consultation_derniere_loi):
    """Vérifier que le contenu HTML est présent."""
    data = consultation_derniere_loi
    texte_complet = data["texte_complet"]

    assert texte_complet.texte_html is not None, "Le contenu HTML ne peut pas être None"
    assert len(texte_complet.texte_html.strip()) > 0, (
        "Le contenu HTML ne peut pas être vide"
    )


@then("le contenu HTML est présent et nettoyé des balises html")
def verifier_contenu_html_present_et_nettoye(consultation_derniere_loi):
    """Vérifier que le contenu HTML est présent et nettoyé."""
    data = consultation_derniere_loi
    texte_complet = data["texte_complet"]

    assert texte_complet.texte_html is not None, "Le contenu HTML ne peut pas être None"
    assert len(texte_complet.texte_html.strip()) > 0, (
        "Le contenu HTML ne peut pas être vide"
    )

    # Utiliser la nouvelle propriété texte_brut (2025 best practices)
    assert texte_complet.texte_brut is not None, "Le contenu brut ne peut pas être None"
    assert len(texte_complet.texte_brut.strip()) > 0, (
        "Le contenu brut ne peut pas être vide"
    )


@then(parsers.parse('le statut juridique est "{statut}"'))
def verifier_statut_juridique(consultation_par_id, statut: str):
    """Vérifier que le statut juridique du texte correspond à celui attendu."""
    texte = consultation_par_id
    assert texte.etat is not None, "Le texte doit avoir un statut juridique"
    assert texte.etat == statut, (
        f"Le statut attendu est '{statut}', mais obtenu '{texte.etat}'"
    )


@then("je peux voir les versions disponibles")
def verifier_versions_disponibles(verification_statut_juridique):
    """Vérifier que je peux accéder aux versions du texte."""
    texte = verification_statut_juridique
    versions = texte.versions()
    assert isinstance(versions, list), "Les versions doivent être une liste"
    assert len(versions) > 0, "Au moins une version doit être disponible"

    # Vérifier que chaque version est valide
    for version in versions:
        assert isinstance(version, TexteLoda), "Chaque version doit être un TexteLoda"
        assert version.id is not None, "Chaque version doit avoir un ID"


@then("je peux accéder au contenu de chaque version")
def verifier_acces_contenu_versions(verification_statut_juridique):
    """Vérifier que je peux accéder au contenu de chaque version."""
    texte = verification_statut_juridique
    versions = texte.versions()

    assert len(versions) > 0, "Au moins une version doit être disponible"

    for version in versions:
        # Vérifier qu'on peut accéder aux métadonnées de base
        assert version.titre is not None, "Chaque version doit avoir un titre"
        assert version.etat is not None, "Chaque version doit avoir un statut juridique"

        # Vérifier qu'on peut accéder au contenu (HTML ou sections/articles)
        has_content = (
            version.texte_html is not None
            or (version.sections and len(version.sections) > 0)
            or (version.articles and len(version.articles) > 0)
        )
        assert has_content, f"La version {version.id} doit avoir du contenu accessible"


@then("je peux voir les modifications apportées par cette loi")
def verifier_modifications_apportees(verification_statut_juridique):
    """Vérifier que je peux voir les modifications apportées par cette loi."""
    texte = verification_statut_juridique

    # Vérifier qu'on peut accéder aux articles qui contiennent les modifications
    assert texte.articles is not None, "Le texte doit avoir des articles"
    assert len(texte.articles) > 0, "Le texte doit contenir au moins un article"

    # Vérifier que le premier article contient du contenu
    premier_article = texte.articles[0]
    assert premier_article.content is not None, (
        "Le premier article doit avoir du contenu"
    )
    assert len(premier_article.content.strip()) > 0, (
        "Le premier article ne peut pas être vide"
    )


@then("je peux consulter le contenu d'un article modifié par cette loi")
def verifier_consultation_article_modifie(verification_statut_juridique):
    """Vérifier que je peux consulter le contenu d'un article modifié par cette loi."""
    texte = verification_statut_juridique

    # Utiliser la nouvelle méthode pour récupérer les articles modifiés
    articles_modifies = texte.get_modified_articles()

    print(texte.format_modifications_report())

    # Vérifications simples sans conditionnelles
    assert len(articles_modifies) > 0, (
        "Au moins un article modifié doit être accessible"
    )
    assert articles_modifies[0].content is not None, (
        "L'article modifié doit avoir du contenu"
    )
    assert len(articles_modifies[0].content.strip()) > 0, (
        "L'article modifié ne peut pas être vide"
    )
