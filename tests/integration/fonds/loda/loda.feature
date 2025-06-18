# language: fr
Fonctionnalité: API LODA - Recherche et consultation de textes légaux
  En tant qu'utilisateur de l'API LODA
  Je veux pouvoir rechercher et consulter des textes légaux
  Afin d'accéder aux informations juridiques

  Contexte:
    Étant donné que l'API Légifrance est accessible
    Et qu'un client API est configuré

  Scénario: Recherche simple par terme
    Lorsque j'appelle loda.search avec le terme "télétravail"
    Alors l'API retourne une liste de TexteLoda
    Et les résultats contiennent le terme recherché

  Scénario: Recherche par nature LOI
    Lorsque j'appelle loda.search avec la nature "LOI"
    Alors l'API retourne uniquement des lois
    Et chaque résultat a la nature "LOI"

  Scénario: Recherche par nature DECRET
    Lorsque j'appelle loda.search avec la nature "DECRET"
    Alors l'API retourne uniquement des décrets
    Et chaque résultat a la nature "DECRET"

  Scénario: Recherche par nature ORDONNANCE
    Lorsque j'appelle loda.search avec la nature "ORDONNANCE"
    Alors l'API retourne uniquement des ordonnances
    Et chaque résultat a la nature "ORDONNANCE"

  Scénario: Recherche par nature ARRETE
    Lorsque j'appelle loda.search avec la nature "ARRETE"
    Alors l'API retourne uniquement des arrêtés
    Et chaque résultat a la nature "ARRETE"

  Scénario: Consultation par ID
    Lorsque j'appelle loda.fetch avec l'ID "LEGITEXT000006069570"
    Alors l'API retourne un TexteLoda unique
    Et l'objet contient les métadonnées complètes

  Plan du scénario: Pagination basique
    Lorsque j'appelle loda.search avec page_size=<taille_page>
    Alors l'API retourne au maximum <taille_page> résultats
    Et la pagination fonctionne correctement

    Exemples:
      | taille_page |
      | 5           |
      | 10          |

  Scénario: Recherche avec date de début
    Lorsque j'appelle loda.search avec date_debut="2023-01-01"
    Alors tous les résultats ont une date >= "2023-01-01"
    Et aucun résultat antérieur n'est retourné

  Scénario: Recherche avec date de fin
    Lorsque j'appelle loda.search avec date_fin="2023-12-31"
    Alors tous les résultats ont une date <= "2023-12-31"
    Et aucun résultat postérieur n'est retourné

  Scénario: Recherche par fond LODA_DATE
    Lorsque j'appelle loda.search avec le fond "LODA_DATE"
    Alors l'API utilise le fond spécialisé pour les dates
    Et les résultats correspondent aux versions historiques

  Scénario: Recherche par fond LODA_ETAT
    Lorsque j'appelle loda.search avec le fond "LODA_ETAT"
    Alors l'API utilise le fond spécialisé pour les états
    Et les résultats correspondent aux statuts juridiques

  Scénario: Formatage désactivé par défaut
    Lorsque j'appelle loda.search sans formatter
    Alors les résultats ne contiennent pas d'URLs formatées
    Et les données brutes sont retournées

  Scénario: Formatage activé
    Lorsque j'appelle loda.search avec formatter=True
    Alors les résultats contiennent des URLs enrichies
    Et les métadonnées sont formatées

  Scénario: Gestion d'erreur nature invalide
    Lorsque j'appelle loda.search avec la nature invalide "INVALIDE"
    Alors l'API lève une erreur de validation
    Et le message indique les natures valides