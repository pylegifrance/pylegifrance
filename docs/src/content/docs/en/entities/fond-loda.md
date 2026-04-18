---
title: Fond LODA
description: Facade for laws, ordinances, decrees and orders.
sidebar:
  order: 6
---

The `Loda` class (in `pylegifrance/fonds/loda.py`) exposes the **LODA** fond
(Lois, Ordonnances, Décrets, Arrêtés) via two Legifrance bases:

- `LODA_ETAT` — current state;
- `LODA_DATE` — historical state (default in the facade).

## Scope and filtering

By default, the search is limited to texts in force as of today:

- facet `DATE_VERSION` = today,
- facets `TEXT_LEGAL_STATUS` and `ARTICLE_LEGAL_STATUS` = `VIGUEUR`,

regardless of the target fond (`LODA_DATE` or `LODA_ETAT`).

The text type is narrowed via `SearchRequest.nature` (default
`["LOI", "ORDONNANCE", "DECRET", "ARRETE"]`).

## Usage

```python
from pylegifrance.client import LegifranceClient
from pylegifrance.fonds.loda import Loda
from pylegifrance.models.loda.search import SearchRequest

client = LegifranceClient()
loda = Loda(client)

# Simplified search
results = loda.search("environnement")

# Structured search
results = loda.search(
    SearchRequest(
        search="environnement",
        page_number=2,
        page_size=20,
    )
)

# Version of a text at a specific date
versioned = loda.fetch_version_at("78-17", "2022-01-01")

# All versions of a text
versions = loda.fetch_versions("78-17")
```

## See also

- [How-to: search in LODA](/pylegifrance/en/operations/search-loda/)
- [API reference](/pylegifrance/en/references/loda/)

:::caution
It is the user's sole responsibility to verify that the information returned
by the API is relevant and up to date.
:::
