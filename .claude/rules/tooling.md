# Tooling

## UV (Package Manager)

```bash
uv sync                  # Install/update all dependencies
uv run <cmd>             # Run command in the venv
uv build                 # Build distribution
uv add <pkg>             # Add a dependency
```

## Ruff (Lint + Format)

```bash
uv run ruff check .              # Lint
uv run ruff check . --fix        # Lint with auto-fix
uv run ruff format .             # Format
```

Config: `pyproject.toml` under `[tool.ruff]`.

## ty (Type Checker)

```bash
uvx ty check             # Type check
```

Config: `pyproject.toml` under `[tool.ty]` — `python-version = "3.12"`, includes `pylegifrance/`.

## Pre-commit

```bash
uv run pre-commit run --all-files
```

Hook order:
1. `validate-pyproject` — validates `pyproject.toml`
2. `prettier` — formats YAML/JSON
3. `ruff` — lint with `--fix --exit-non-zero-on-fix`
4. `ruff-format` — format
5. `ty` — local hook running `uvx ty check`

## MkDocs (Documentation)

```bash
uv run mkdocs serve      # Local dev server
uv run mkdocs build      # Build static site
```

Optional deps must be installed first: `uv sync --group docs` or `uv sync --all-groups`.

## GitHub Actions

- **Tests**: Run on push to any branch.
- **Release**: Triggered by version tags.

## Version Management

Version is in `pyproject.toml` under `[project]` → `version`. Update it there directly.
