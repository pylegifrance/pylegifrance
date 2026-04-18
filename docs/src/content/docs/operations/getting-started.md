---
title: Démarrage rapide
description: Premier script PyLegifrance en 5 minutes.
sidebar:
  order: 1
---

## 1. Prérequis

- Python 3.12+.
- Un compte PISTE avec l'API Legifrance souscrite — voir
  [`/operations/create-piste-account`](/pylegifrance/operations/create-piste-account/).
- Vos identifiants dans un `.env` — voir
  [`/operations/configure-api-credentials`](/pylegifrance/operations/configure-api-credentials/).

## 2. Installer

```bash
uv add pylegifrance
```

## 3. Premier script

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.code import Code
from pylegifrance.models.code.enum import NomCode

client = LegifranceClient()             # lit .env
code = Code(client)

# Article 1382 du Code civil
resultat = (
    code.search()
        .in_code(NomCode.CC)
        .article_number("1382")
        .execute()
)

print(resultat)
```

## 4. Exemples suivants

### Recherche par mot-clé

```python
from pylegifrance.fonds.loda import Loda
from pylegifrance.models.loda.search import SearchRequest

loda = Loda(client)

resultats = loda.search(
    SearchRequest(
        text_id="78-17",
        champ="ARTICLE",
        type_recherche="TOUS_LES_MOTS_DANS_UN_CHAMP",
    )
)
```

### Filtre par date et nature

```python
resultats = loda.search(
    SearchRequest(
        search="environnement",
        champ="TITLE",
        nature=["DECRET"],
        date_signature=["2022-01-01", "2022-12-31"],
    )
)
```

### Formatage lisible

```python
resultat = (
    code.search()
        .in_code(NomCode.CC)
        .article_number("16")
        .with_formatter()
        .execute()
)
```

## Pour aller plus loin

- [Rechercher dans les codes](/pylegifrance/operations/search-legal-code/)
- [Récupérer une décision](/pylegifrance/operations/fetch-case-law/)
- [Rechercher dans LODA](/pylegifrance/operations/search-loda/)
- [Builder pattern](/pylegifrance/concepts/builder-pattern/)
