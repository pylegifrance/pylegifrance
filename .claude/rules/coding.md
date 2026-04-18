# Coding Conventions

> Every rule below cites the section of the official documentation that
> grounds it. **Read the linked source before modifying any rule here.**

## Formatting (Ruff)

> Source: [Ruff Formatter](https://docs.astral.sh/ruff/formatter/) and
> [Formatter configuration](https://docs.astral.sh/ruff/formatter/#configuration).

- Line length: 88
- Quote style: double
- Indent style: spaces
- Target version: `py312`

## Lint Rules (Ruff)

> Source: [Ruff — Rules index](https://docs.astral.sh/ruff/rules/). Each
> code maps to a section in that index (e.g. `E` → pycodestyle errors,
> `UP` → pyupgrade).

Enabled rule sets: `E` (pycodestyle errors), `W` (pycodestyle warnings),
`F` (Pyflakes), `I` (isort), `B` (flake8-bugbear),
`C4` (flake8-comprehensions), `UP` (pyupgrade).

`E501` is ignored (handled by formatter).

isort knows `pylegifrance` as first-party.

## Docstrings

> Source: [Google Python Style Guide — §3.8 Comments and Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

Use Google-style docstrings:

```python
def fetch_article(self, article_id: str) -> ArticleFetcher:
    """Short summary in imperative mood.

    Args:
        article_id: Description of the parameter.

    Returns:
        Description of the return value.

    Raises:
        ValueError: When the input is invalid.
    """
```

## Type Hints

> Sources:
>
> - [`typing.Self`](https://docs.python.org/3/library/typing.html#typing.Self) (PEP 673).
> - [PEP 604 — `X | Y` union syntax](https://peps.python.org/pep-0604/).
> - [PEP 585 — generic builtins (`list[...]`, `dict[...]`)](https://peps.python.org/pep-0585/).

- Use `Self` (from `typing`) for builder / fluent return types.
- Use `X | None` union syntax (Python 3.12+).
- Use `list[...]`, `dict[...]` (lowercase builtins; no `typing.List`).

## Pydantic v2 Patterns

> Sources:
>
> - [Pydantic — Models](https://docs.pydantic.dev/latest/concepts/models/).
> - [Pydantic — `ConfigDict`](https://docs.pydantic.dev/latest/api/config/).
> - [Pydantic — Alias generators](https://docs.pydantic.dev/latest/concepts/alias/#alias-generator).
> - [Pydantic — `model_dump`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_dump).

- All domain models extend `PyLegifranceBaseModel`
  (in @pylegifrance/models/base.py).
- `PyLegifranceBaseModel` uses `ConfigDict` with
  `alias_generator=to_camel` and `populate_by_name=True`.
- Serialize with `model_dump(by_alias=True, mode="json")` for API
  payloads.
- Individual models may override with their own `ConfigDict` adding
  `validate_by_name=True, validate_by_alias=True`.

## Enum Wrapping Pattern

> @docs/src/content/docs/concepts/enum-wrapping.md
