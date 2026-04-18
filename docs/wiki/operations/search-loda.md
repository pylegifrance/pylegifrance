---
title: Rechercher dans LODA
description: Recherche dans le fond Lois / Ordonnances / Décrets / Arrêtés.
sidebar:
  order: 7
---

La classe [`Loda`](/pylegifrance/entities/fond-loda/) permet d'interroger le fond LODA.

## Recherche simple

```python
from pylegifrance.client import LegifranceClient
from pylegifrance.fonds.loda import Loda

client = LegifranceClient()
loda = Loda(client)

resultats = loda.search("environnement")
```

## Recherche structurée

```python
from pylegifrance.models.loda.search import SearchRequest

resultats = loda.search(
    SearchRequest(
        search="environnement",
        page_number=2,
        page_size=20,
    )
)
```

## Version à une date

```python
texte = loda.fetch_version_at("78-17", "2022-01-01")
```

## Toutes les versions d'un texte

```python
versions = loda.fetch_versions("78-17")
```

## Portée par défaut

- Seuls les textes **en vigueur** à la date du jour sont retournés.
- `nature` est restreinte à `["LOI", "ORDONNANCE", "DECRET", "ARRETE"]`.

Voir [`/entities/fond-loda`](/pylegifrance/entities/fond-loda/) pour les détails.

## Voir aussi

- [`/references/loda`](/pylegifrance/references/loda/)

:::caution
Il est de la responsabilité exclusive de l'utilisateur·rice de vérifier
que les informations renvoyées par l'API sont pertinentes et à jour.
:::
