---
title: Search in LODA
description: Search the Laws / Ordinances / Decrees / Orders fond.
sidebar:
  order: 7
---

The [`Loda`](/pylegifrance/en/entities/fond-loda/) class lets you query the
LODA fond.

## Simple search

```python
from pylegifrance.client import LegifranceClient
from pylegifrance.fonds.loda import Loda

client = LegifranceClient()
loda = Loda(client)

results = loda.search("environnement")
```

## Structured search

```python
from pylegifrance.models.loda.search import SearchRequest

results = loda.search(
    SearchRequest(
        search="environnement",
        page_number=2,
        page_size=20,
    )
)
```

## Version at a date

```python
text = loda.fetch_version_at("78-17", "2022-01-01")
```

## All versions of a text

```python
versions = loda.fetch_versions("78-17")
```

## Default scope

- Only texts **in force** as of today are returned.
- `nature` is limited to `["LOI", "ORDONNANCE", "DECRET", "ARRETE"]`.

See [`/en/entities/fond-loda`](/pylegifrance/en/entities/fond-loda/) for
details.

## See also

- [`/en/references/loda`](/pylegifrance/en/references/loda/)

:::caution
It is the user's sole responsibility to verify that the information
returned by the API is relevant and up to date.
:::
