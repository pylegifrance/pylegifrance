---
title: Quick start
description: Your first PyLegifrance script in 5 minutes.
sidebar:
  order: 1
---

## 1. Prerequisites

- Python 3.12+.
- A PISTE account with the Legifrance API subscription — see
  [/en/operations/create-piste-account](/pylegifrance/en/operations/create-piste-account/).
- Your credentials in a `.env` file — see
  [/en/operations/configure-api-credentials](/pylegifrance/en/operations/configure-api-credentials/).

## 2. Install

```bash
uv add pylegifrance
```

## 3. First script

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.code import Code
from pylegifrance.models.code.enum import NomCode

client = LegifranceClient()             # reads .env
code = Code(client)

# Article 1382 of the Code civil
result = (
    code.search()
        .in_code(NomCode.CC)
        .article_number("1382")
        .execute()
)

print(result)
```

## 4. More examples

### Keyword search

```python
from pylegifrance.fonds.loda import Loda
from pylegifrance.models.loda.search import SearchRequest

loda = Loda(client)

results = loda.search(
    SearchRequest(
        text_id="78-17",
        champ="ARTICLE",
        type_recherche="TOUS_LES_MOTS_DANS_UN_CHAMP",
    )
)
```

### Filter by date and nature

```python
results = loda.search(
    SearchRequest(
        search="environnement",
        champ="TITLE",
        nature=["DECRET"],
        date_signature=["2022-01-01", "2022-12-31"],
    )
)
```

### Readable formatting

```python
result = (
    code.search()
        .in_code(NomCode.CC)
        .article_number("16")
        .with_formatter()
        .execute()
)
```

## Next steps

- [Search in legal codes](/pylegifrance/en/operations/search-legal-code/)
- [Fetch a case law decision](/pylegifrance/en/operations/fetch-case-law/)
- [Search in LODA](/pylegifrance/en/operations/search-loda/)
- [Builder pattern](/pylegifrance/en/concepts/builder-pattern/)
