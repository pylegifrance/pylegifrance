---
title: Code
description: Référence de la façade Code (recherche et consultation des codes français).
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

| Méthode | Signature | Rôle |
|---|---|---|
| `in_code` | `(code_name: NomCode) -> Self` | restreindre à un code |
| `in_codes` | `(code_names: list[str | NomCode]) -> Self` | plusieurs codes |
| `article_number` | `(number: str) -> Self` | par numéro d'article |
| `text` | `(search_text: str, in_field: TypeChampCode = TypeChampCode.ALL) -> Self` | recherche textuelle |
| `at_date` | `(date_str: str) -> Self` | `YYYY-MM-DD` |
| `with_legal_status` | `(status: list[EtatJuridique] = [EtatJuridique.VIGUEUR]) -> Self` | filtrer par état |
| `with_formatter` | `() -> Self` | activer formatage |
| `paginate` | `(page_number: int = 1, page_size: int = 10) -> Self` | pagination |
| `execute` | `() -> list[Article]` | exécuter |

Valeurs possibles pour `in_field` :

- `TypeChampCode.NUM_ARTICLE`
- `TypeChampCode.TITLE`
- `TypeChampCode.TEXT`
- `TypeChampCode.ALL` (défaut)

## Exceptions

- `ValueError` — paramètres invalides.
- `Exception` — échec de l'appel API.

## Voir aussi

- [`/entities/fond-code`](/pylegifrance/entities/fond-code/)
- [`/operations/search-legal-code`](/pylegifrance/operations/search-legal-code/)
- [`/concepts/builder-pattern`](/pylegifrance/concepts/builder-pattern/)
