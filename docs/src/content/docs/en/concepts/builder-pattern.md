---
title: Builder pattern
description: Fluent API to compose readable, typed search requests.
sidebar:
  order: 2
---

Each facade exposes a **fluent builder** that composes a request by method
chaining, terminated by `.execute()`.

## Example: `Code.search()`

```python
results = (
    code.search()
        .in_code(NomCode.CC)
        .article_number("1382")
        .with_formatter()
        .execute()
)
```

Builders return `Self` to allow chaining; they take the
[`LegifranceClient`](/pylegifrance/en/entities/legifrance-client/) as the
first argument.

## Existing builders

| Builder | Entry point | Typical methods |
|---|---|---|
| `CodeSearchBuilder` | `Code.search()` | `.in_code()`, `.text()`, `.article_number()`, `.at_date()`, `.with_formatter()`, `.paginate()`, `.execute()` |
| `CodeConsultFetcher` | `Code.fetch_code(id)` | `.include_abrogated()`, `.section()`, `.at(date)` |
| `ArticleFetcher` | `Code.fetch_article(id)` | `.at(date)` |

## Why a builder instead of a big `dataclass`?

- **Readability**: the request reads like a sentence.
- **Progressivity**: each step is optional and composable.
- **Typing**: each method narrows the permissible parameters (e.g. `in_code`
  accepts a `NomCode`, not a `str`).
- **Discoverability**: autocompletion guides the user towards valid methods.

## See also

- [`/en/entities/fond-code`](/pylegifrance/en/entities/fond-code/)
- [API reference `/en/references/code`](/pylegifrance/en/references/code/)
