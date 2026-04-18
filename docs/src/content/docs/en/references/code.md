---
title: Code
description: Reference for the Code facade (search and consult French legal codes).
sidebar:
  order: 3
---

## Code

```python
class Code:
    def __init__(client: LegifranceClient, fond: str = "CODE_ETAT")
    def search() -> CodeSearchBuilder
    def fetch_code(text_id: str) -> CodeConsultFetcher
    def fetch_article(article_id: str) -> ArticleFetcher
```

## CodeSearchBuilder

| Method | Signature | Role |
|---|---|---|
| `in_code` | `(code_name: NomCode) -> Self` | restrict to one code |
| `in_codes` | `(code_names: list[str | NomCode]) -> Self` | multiple codes |
| `article_number` | `(number: str) -> Self` | by article number |
| `text` | `(search_text: str, in_field: TypeChampCode = TypeChampCode.ALL) -> Self` | full-text search |
| `at_date` | `(date_str: str) -> Self` | `YYYY-MM-DD` |
| `with_legal_status` | `(status: list[EtatJuridique] = [EtatJuridique.VIGUEUR]) -> Self` | filter by status |
| `with_formatter` | `() -> Self` | enable formatting |
| `paginate` | `(page_number: int = 1, page_size: int = 10) -> Self` | pagination |
| `execute` | `() -> list[Article]` | execute |

Allowed values for `in_field`:

- `TypeChampCode.NUM_ARTICLE`
- `TypeChampCode.TITLE`
- `TypeChampCode.TEXT`
- `TypeChampCode.ALL` (default)

## Exceptions

- `ValueError` — invalid parameters.
- `Exception` — API call failure.

## See also

- [`/en/entities/fond-code`](/pylegifrance/en/entities/fond-code/)
- [`/en/operations/search-legal-code`](/pylegifrance/en/operations/search-legal-code/)
- [`/en/concepts/builder-pattern`](/pylegifrance/en/concepts/builder-pattern/)
