---
title: Rechercher dans les codes
description: Exemples d'usage du builder Code.search() — article par numéro, mot-clé, historique, pagination.
sidebar:
  order: 5
---

La classe [`Code`](/pylegifrance/entities/fond-code/) expose un builder fluide —
[voir le pattern](/pylegifrance/concepts/builder-pattern/).

## Article par numéro

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.code import Code
from pylegifrance.models.code.enum import NomCode

client = LegifranceClient()
code = Code(client)

resultats = (
    code.search()
        .in_code(NomCode.CC)
        .article_number("7")
        .execute()
)
```

## Avec formatage

```python
resultats = (
    code.search()
        .in_code(NomCode.CC)
        .article_number("7")
        .with_formatter()
        .execute()
)
```

## Code entier

```python
resultats = (
    code.search()
        .in_code(NomCode.CC)
        .execute()
)
```

## Recherche par mot dans le texte

```python
from pylegifrance.models.code.enum import TypeChampCode

resultats = (
    code.search()
        .in_code(NomCode.CC)
        .text("responsabilité", in_field=TypeChampCode.ARTICLE)
        .paginate(page_size=20)
        .execute()
)
```

## Recherche historique

```python
# Code civil au 1er janvier 2000
resultats = (
    code.search()
        .in_code(NomCode.CC)
        .at_date("2000-01-01")
        .execute()
)
```

Par défaut la recherche porte sur l'état en vigueur. Pour l'historique
chronique, initialiser avec `Code(client, fond="CODE_DATE")` ou utiliser
`.at_date()`.

## Pagination

```python
resultats = (
    code.search()
        .in_code(NomCode.CC)
        .text("contrat")
        .paginate(page_number=1, page_size=20)
        .execute()
)
```

## Forme du retour

`execute()` renvoie une `list[Article]` (modèle Pydantic). Voir
[`/entities/article`](/pylegifrance/entities/article/) pour les champs
disponibles. Exemple d'accès :

```python
for article in resultats:
    print(article.id, article.num, article.title)
```

## Voir aussi

- [`/entities/fond-code`](/pylegifrance/entities/fond-code/)
- [`/references/code`](/pylegifrance/references/code/)

:::caution
Il est de la responsabilité exclusive de l'utilisateur·rice de vérifier
que les informations renvoyées par l'API sont pertinentes et à jour.
:::
