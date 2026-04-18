---
title: Fond Code
description: Facade to search and consult French legal codes (Code civil, Code pénal, etc.).
sidebar:
  order: 4
---

The `Code` class (in `pylegifrance/fonds/code.py`) is the facade that exposes
the fluent API for searching French codes.

## Scope

The fond groups the codes (Code civil, Code pénal, Code de commerce…) served
via two Legifrance bases:

- `CODE_ETAT` — current state of the codes (default);
- `CODE_DATE` — historical state at a given date.

By default, searches target articles in force as of today. For a historical
search, use
[`.at_date("YYYY-MM-DD")`](/pylegifrance/en/concepts/builder-pattern/) or
initialize with `Code(client, fond="CODE_DATE")`.

## Usage

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.code import Code
from pylegifrance.models.code.enum import NomCode

client = LegifranceClient(client_id="...", client_secret="...")
code = Code(client)

# Article 1382 of the Code civil
results = (
    code.search()
        .in_code(NomCode.CC)
        .article_number("1382")
        .execute()
)
```

## Exposed components

- `code.search()` → `CodeSearchBuilder` (fluent, see
  [`/en/concepts/builder-pattern`](/pylegifrance/en/concepts/builder-pattern/)).
- `code.fetch_code(text_id)` → consult of an entire LEGITEXT.
- `code.fetch_article(article_id)` → article by LEGIARTI.

## Common codes

| Enum | Code | LEGITEXT |
|---|---|---|
| `NomCode.CC` | Code civil | `LEGITEXT000006070721` |
| `NomCode.CP` | Code pénal | `LEGITEXT000006070719` |
| `NomCode.CCOM` | Code de commerce | `LEGITEXT000005634379` |
| `NomCode.CTRAV` | Code du travail | `LEGITEXT000006072050` |
| `NomCode.CPC` | Code de procédure civile | `LEGITEXT000006070716` |
| `NomCode.CPP` | Code de procédure pénale | `LEGITEXT000006071154` |

Full list: [legifrance.gouv.fr/liste/code?etatTexte=VIGUEUR](https://www.legifrance.gouv.fr/liste/code?etatTexte=VIGUEUR).

## See also

- [How-to: search in the codes](/pylegifrance/en/operations/search-legal-code/)
- [API reference](/pylegifrance/en/references/code/)
- [`/en/concepts/enum-wrapping`](/pylegifrance/en/concepts/enum-wrapping/) —
  why `NomCode` isn't the generated enum directly.

:::caution
It is the user's sole responsibility to verify that the information returned
by the API is relevant and up to date.
:::
