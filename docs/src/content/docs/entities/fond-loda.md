---
title: Fond LODA
description: Façade pour les lois, ordonnances, décrets et arrêtés.
sidebar:
  order: 6
---

La classe `Loda` (dans `pylegifrance/fonds/loda.py`) expose le fond **LODA**
(Lois, Ordonnances, Décrets, Arrêtés) via deux bases Legifrance :

- `LODA_ETAT` — état actuel ;
- `LODA_DATE` — état historique (par défaut dans la façade).

## Portée et filtrage

Par défaut, la recherche est limitée aux textes en vigueur à la date du jour :

- facette `DATE_VERSION` = aujourd'hui,
- facettes `TEXT_LEGAL_STATUS` et `ARTICLE_LEGAL_STATUS` = `VIGUEUR`,

quel que soit le fond cible (`LODA_DATE` ou `LODA_ETAT`).

Le type de textes est restreint via `SearchRequest.nature` (par défaut
`["LOI", "ORDONNANCE", "DECRET", "ARRETE"]`).

## Usage

```python
from pylegifrance.client import LegifranceClient
from pylegifrance.fonds.loda import Loda
from pylegifrance.models.loda.search import SearchRequest

client = LegifranceClient()
loda = Loda(client)

# Recherche simplifiée
resultats = loda.search("environnement")

# Recherche structurée
resultats = loda.search(
    SearchRequest(
        search="environnement",
        page_number=2,
        page_size=20,
    )
)

# Version d'un texte à une date
texte_version = loda.fetch_version_at("78-17", "2022-01-01")

# Toutes les versions d'un texte
versions = loda.fetch_versions("78-17")
```

## Voir aussi

- [How-to : rechercher dans LODA](/pylegifrance/operations/search-loda/)
- [Référence API](/pylegifrance/references/loda/)

:::caution
Il est de la responsabilité exclusive de l'utilisateur·rice de vérifier que
les informations renvoyées par l'API sont pertinentes et à jour.
:::
