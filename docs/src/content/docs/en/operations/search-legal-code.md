---
title: Search in legal codes
description: Usage examples of the Code.search() builder — article by number, keyword, historical, pagination.
sidebar:
  order: 5
---

The [`Code`](/pylegifrance/en/entities/fond-code/) class exposes a fluent
builder —
[see the pattern](/pylegifrance/en/concepts/builder-pattern/).

## Article by number

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.code import Code
from pylegifrance.models.code.enum import NomCode

client = LegifranceClient()
code = Code(client)

results = (
    code.search()
        .in_code(NomCode.CC)
        .article_number("7")
        .execute()
)
```

## With formatting

```python
results = (
    code.search()
        .in_code(NomCode.CC)
        .article_number("7")
        .with_formatter()
        .execute()
)
```

## Whole code

```python
results = (
    code.search()
        .in_code(NomCode.CC)
        .execute()
)
```

## Keyword search in article text

```python
from pylegifrance.models.code.enum import TypeChampCode

results = (
    code.search()
        .in_code(NomCode.CC)
        .text("responsabilité", in_field=TypeChampCode.TEXT)
        .paginate(page_size=20)
        .execute()
)
```

## Historical search

```python
# Code civil as of January 1st, 2000
results = (
    code.search()
        .in_code(NomCode.CC)
        .at_date("2000-01-01")
        .execute()
)
```

By default the search targets the current state. For a historical view,
initialize with `Code(client, fond="CODE_DATE")` or use `.at_date()`.

## Pagination

```python
results = (
    code.search()
        .in_code(NomCode.CC)
        .text("contrat")
        .paginate(page_number=1, page_size=20)
        .execute()
)
```

## Return shape

`execute()` returns a `list[Article]` (Pydantic model). See
[`/en/entities/article`](/pylegifrance/en/entities/article/) for available
fields. Access example:

```python
for article in results:
    print(article.id, article.num, article.title)
```

## See also

- [`/en/entities/fond-code`](/pylegifrance/en/entities/fond-code/)
- [`/en/references/code`](/pylegifrance/en/references/code/)

:::caution
It is the user's sole responsibility to verify that the information
returned by the API is relevant and up to date.
:::
