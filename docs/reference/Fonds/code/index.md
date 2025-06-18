# Code

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.code import Code

client = LegifranceClient(client_id="...", client_secret="...")
code = Code(client)

# Création d'une requête de recherche
resultats = (code.search()
                .in_code(NomCode.CC)  # Code civil
                .article_number("1382")
                .execute())
```

Interface fluide pour rechercher des articles dans les codes français en utilisant l'API Legifrance.

## Description

La classe `Code` et sa méthode `search()` permettent d'effectuer des recherches dans les codes français (Code civil, Code pénal, etc.) en utilisant une API fluide avec le pattern Builder. Cette approche permet de construire des requêtes complexes de manière lisible et maintenable.

## Initialisation

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.code import Code

client = LegifranceClient(client_id="...", client_secret="...")
code = Code(client, fond="CODE_ETAT")  # ou "CODE_DATE" pour recherche historique
```

## Méthodes principales

### search()

```python
def search() -> CodeSearchBuilder
```

Démarre la construction d'une requête de recherche et retourne un builder pour configurer la recherche.

### fetch_code(text_id)

```python
def fetch_code(text_id: str) -> CodeConsultFetcher
```

Récupère le contenu complet d'un code juridique identifié par son ID LEGITEXT.

### fetch_article(article_id)

```python
def fetch_article(article_id: str) -> ArticleFetcher
```

Récupère un article spécifique identifié par son ID LEGIARTI.

## Méthodes du CodeSearchBuilder

### in_code(code_name)

```python
def in_code(code_name: NomCode) -> Self
```

Filtre la recherche à un code juridique spécifique.

### in_codes(code_names)

```python
def in_codes(code_names: List[Union[str, NomCode]]) -> Self
```

Filtre la recherche à plusieurs codes juridiques.

### article_number(number)

```python
def article_number(number: str) -> Self
```

Recherche un article par son numéro.

### text(search_text, in_field)

```python
def text(search_text: str, in_field: TypeChampCode = TypeChampCode.ALL) -> Self
```

Recherche un texte dans les articles. Le paramètre `in_field` peut être:
- `TypeChampCode.NUM_ARTICLE`: Numéro d'article
- `TypeChampCode.TITLE`: Titre de l'article
- `TypeChampCode.TEXT`: Texte de l'article
- `TypeChampCode.ALL`: Tous les champs (défaut)

### at_date(date_str)

```python
def at_date(date_str: str) -> Self
```

Spécifie une date pour la recherche (format "YYYY-MM-DD").

### with_legal_status(status)

```python
def with_legal_status(status: List[EtatJuridique] = [EtatJuridique.VIGUEUR]) -> Self
```

Filtre par état juridique des articles.

### with_formatter()

```python
def with_formatter() -> Self
```

Active le formatage des résultats pour une meilleure lisibilité.

### paginate(page_number, page_size)

```python
def paginate(page_number: int = 1, page_size: int = 10) -> Self
```

Configure la pagination des résultats.

### execute()

```python
def execute() -> Dict
```

Exécute la recherche et retourne les résultats.

## Structure des résultats

```python
{
    "results": [
        {
            "id": "LEGIARTI000006419305",
            "title": "Article 1",
            "text": "Contenu de l'article...",
            "num": "1",
            "etat": "VIGUEUR",
            "date_version": "2023-01-01",
            "liens": [...]
        },
        # Autres résultats...
    ],
    "pagination": {
        "page": 1,
        "pageSize": 10,
        "total": 42
    }
}
```

## Exceptions

- `ValueError`: Si les paramètres fournis sont invalides.
- `Exception`: Si l'appel à l'API échoue.

## Exemples

### Recherche d'un article par numéro dans le Code civil

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.code import Code
from pylegifrance.models.code.enum import NomCode

client = LegifranceClient(client_id="...", client_secret="...")
code = Code(client)

# Recherche de l'article 1382 du Code civil
resultats = (code.search()
                .in_code(NomCode.CC)  # Code civil
                .article_number("1382")
                .with_formatter()
                .execute())

# Affichage du premier résultat
if resultats["results"]:
    article = resultats["results"][0]
    print(f"Article {article['num']}: {article['title']}")
    print(article['text'])
```

### Recherche par mot-clé dans le texte des articles

```python
from pylegifrance.models.code.enum import TypeChampCode

# Recherche des articles contenant le mot "responsabilité" dans le Code civil
resultats = (code.search()
                .in_code(NomCode.CC)  # Code civil
                .text("responsabilité", in_field=TypeChampCode.TEXT)
                .paginate(page_size=20)
                .execute())

# Affichage du nombre de résultats
print(f"Nombre de résultats: {resultats['pagination']['total']}")
```

### Recherche historique à une date spécifique

```python
# Recherche dans le Code civil tel qu'il était au 1er janvier 2000
resultats = (code.search()
                .in_code(NomCode.CC)
                .at_date("2000-01-01")
                .execute())
```

## Codes fréquemment utilisés

- Code civil: `NomCode.CC` ou "LEGITEXT000006070721"
- Code pénal: `NomCode.CP` ou "LEGITEXT000006070719"
- Code de commerce: `NomCode.CCOM` ou "LEGITEXT000005634379"
- Code du travail: `NomCode.CTRAV` ou "LEGITEXT000006072050"
- Code de procédure civile: `NomCode.CPC` ou "LEGITEXT000006070716"
- Code de procédure pénale: `NomCode.CPP` ou "LEGITEXT000006071154"
