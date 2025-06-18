# language: fr
Fonctionnalité: API Code pour l'accès aux codes juridiques français
  En tant que développeur ou juriste
  Je souhaite accéder aux codes juridiques via l'interface Code
  Afin d'intégrer ces données dans mes applications ou scripts

  Contexte:
    Étant donné que l'API Légifrance est accessible
    Et qu'un client API est configuré
    Et qu'une instance Code est créée avec Code(client)

  Scénario: cherche_article_par_numero
    Lorsque j'appelle code.search avec code_name="Code civil" et search="7"
    Alors l'API retourne une liste d'Article
    Et chaque résultat contient les métadonnées de l'article

  Scénario: Recherche de code complet
    Lorsque j'appelle code.search avec code_name="Code civil" sans search
    Alors l'API retourne la structure hiérarchique du code
    Et les résultats incluent les identifiants des sections

  Scénario: Recherche par terme
    Lorsque j'appelle code.search avec search="mineur" et champ="ARTICLE"
    Alors l'API retourne une liste d'articles correspondants
    Et les résultats sont encapsulés dans des objets Article

  Scénario: Consultation directe par ID
    Lorsque j'appelle code.fetch_code avec un text_id valide
    Alors l'API retourne un objet Article unique
    Et l'objet contient le contenu complet de l'article

  Scénario: Pagination
    Lorsque j'appelle code.search avec page_number=2 et page_size=5
    Alors l'API retourne exactement 5 résultats ou moins
    Et les résultats correspondent à la page 2

  Scénario: Formatage activé
    Lorsque j'appelle code.search avec formatter=True
    Alors chaque Article avec CID contient une URL générée

  Scénario: Validation des paramètres
    Lorsque j'appelle code.search avec code_name="Code inexistant"
    Alors l'API lève une ValueError

  Scénario: Recherche par date de version - CODE_DATE
    Lorsque j'appelle code.search avec fond="CODE_DATE"
    Alors l'API utilise le fond CODE_DATE pour la recherche par date de version
    Et les résultats correspondent aux versions à la date spécifiée

  Scénario: Recherche par état juridique - CODE_ETAT
    Lorsque j'appelle code.search avec fond="CODE_ETAT"
    Alors l'API utilise le fond CODE_ETAT pour la recherche par état juridique
    Et les résultats correspondent aux textes en vigueur, abrogés ou modifiés
