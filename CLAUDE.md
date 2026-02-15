# pylegifrance

Python wrapper for the French Legifrance API. Synchronous, `requests`-based, Pydantic v2 models.
Requires Python 3.12+.

## Quick Reference

| Task | Command |
|------|---------|
| Install | `uv sync` |
| Test | `uv run pytest` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| Type check | `uvx ty check` |
| Pre-commit | `uv run pre-commit run --all-files` |
| Docs | `uv run mkdocs serve` |

## Rules

@.claude/rules/coding.md
@.claude/rules/testing.md
@.claude/rules/architecture.md
@.claude/rules/tooling.md

## Environment

Credentials are stored in `.env` (LEGIFRANCE_CLIENT_ID, LEGIFRANCE_CLIENT_SECRET).
**Never read, log, or commit `.env` files.**
