---
title: Loda
description: Référence de la façade Loda (lois, ordonnances, décrets, arrêtés).
sidebar:
  order: 5
---

## Loda

```python
class Loda:
    def __init__(self, client: LegifranceClient)
    def fetch(self, text_id: str) -> TexteLoda | None
    def fetch_version_at(self, text_id: str, date: str) -> TexteLoda | None
    def fetch_versions(self, text_id: str) -> list[TexteLoda]
    def search(self, query: SearchRequest | str) -> list[TexteLoda]
```

## SearchRequest

```python
class SearchRequest:
    text_id: str = ""
    search: str | None = None
    champ: str = "NUM_ARTICLE"
    type_recherche: str = "EXACTE"
    fond: str = "LODA_DATE"
    nature: list[str] = ["LOI", "ORDONNANCE", "DECRET", "ARRETE"]
    date_signature: list[str] | None = None
    page_number: int = 1
    page_size: int = 10
```

Construit des requêtes avancées pour le fond LODA.

## Voir aussi

- [`/entities/fond-loda`](/pylegifrance/entities/fond-loda/)
- [`/operations/search-loda`](/pylegifrance/operations/search-loda/)
