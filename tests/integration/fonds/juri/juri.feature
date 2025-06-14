# language: fr
Fonctionnalité: Recherche de décisions juridiques via l'API Légifrance
  En tant qu'utilisateur de l'API Légifrance
  Je veux pouvoir rechercher et filtrer des décisions de justice
  Afin d'obtenir des informations juridiques pertinentes

  Contexte:
    Étant donné que l'API Légifrance est accessible
    Et qu'un client API est configuré

  Scénario: Recherche_par_mots_cles
    Lorsque je recherche des décisions contenant "responsabilité civile"
    Alors je reçois une liste de décisions pertinentes
    Et chaque décision contient les informations essentielles (juridiction, date, numéro)

  Scénario: Filtrage_par_juridiction
    Lorsque je recherche des décisions de la Cour de cassation
    Alors je ne reçois que des décisions de cette juridiction

  Scénario: Pagination_des_resultats
    Lorsque je recherche des décisions avec une limite de 5 par page
    Alors je reçois exactement 5 résultats
    Et je peux accéder à la page suivante

  Scénario: Extraction_champs_specifiques
    Lorsque je recherche des décisions en spécifiant les champs à extraire
    Alors je reçois uniquement les champs demandés pour chaque décision