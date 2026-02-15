# Coding Conventions

## Formatting (Ruff)

- Line length: 88
- Quote style: double
- Indent style: spaces
- Target version: `py312`

## Lint Rules (Ruff)

Enabled rule sets: `E` (pycodestyle errors), `W` (pycodestyle warnings), `F` (Pyflakes), `I` (isort), `B` (flake8-bugbear), `C4` (flake8-comprehensions), `UP` (pyupgrade).

`E501` is ignored (handled by formatter).

isort knows `pylegifrance` as first-party.

## Docstrings

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

- Use `Self` (from `typing`) for builder/fluent return types.
- Use `X | None` union syntax (Python 3.12+).
- Use `list[...]`, `dict[...]` (lowercase builtins, no `typing.List`).

## Pydantic v2 Patterns

- All domain models extend `PyLegifranceBaseModel` (in `pylegifrance/models/base.py`).
- `PyLegifranceBaseModel` uses `ConfigDict` with `alias_generator=to_camel` and `populate_by_name=True`.
- Serialize with `model_dump(by_alias=True, mode="json")` for API payloads.
- Individual models may override with their own `ConfigDict` adding `validate_by_name=True, validate_by_alias=True`.

## Enum Wrapping Pattern

Domain enums (e.g. `NomCode`, `TypeChampCode`) wrap generated DTO enums from `models/generated/model.py`.
Each domain model provides `to_generated()` to convert to the DTO form and, where needed, a `from_generated()` classmethod for the reverse.
