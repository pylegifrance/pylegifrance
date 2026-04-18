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
uv run pre-commit install          # installs both pre-commit + commit-msg hooks
uv run pre-commit run --all-files  # run every pre-commit hook on the whole tree
```

`default_install_hook_types: [pre-commit, commit-msg]` in
`.pre-commit-config.yaml` wires both stages in one install.

Hook order:

1. `conventional-pre-commit` (commit-msg stage) — rejects commit messages
   that don't match Conventional Commits. Allowed types are the same set
   as `.github/release-please-config.json` plus `revert`.
2. `validate-pyproject` — validates `pyproject.toml`.
3. `prettier` — formats YAML / JSON.
4. `ruff` — lint with `--fix --exit-non-zero-on-fix`.
5. `ruff-format` — format.
6. `ty` — local hook running `uvx ty check`.

## Commit messages

Must follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
Used both by the pre-commit hook (local gate) and by release-please
(changelog + version bump). Per-type effect on the next release:

| Prefix | Release bump | Changelog section |
|---|---|---|
| `feat:` | minor | Features |
| `fix:` | patch | Bug Fixes |
| `perf:` | patch | Performance |
| `refactor:` | patch | Refactoring |
| `docs:` | patch | Documentation |
| `feat!:` or `BREAKING CHANGE:` footer | major | Features (flagged) |
| `ci:` / `chore:` / `test:` / `build:` / `style:` / `revert:` | no bump | hidden |

Commits should include a `References:` section with official docs URLs
justifying implementation choices (see repo-root `CLAUDE.md`).

## Documentation (Astro Starlight)

The docs site is an Astro + Starlight project under `docs/` (Node
tooling, pnpm). It is **not** part of the Python package; `uv sync` no
longer installs docs dependencies.

```bash
cd docs
pnpm install             # first-time
pnpm dev                 # http://localhost:4321/pylegifrance
pnpm build               # static output in docs/dist/
```

French is the default locale (served at `/pylegifrance/`); English
mirror lives under `/pylegifrance/en/` with automatic fallback to
French for untranslated pages. The `starlight-llms-txt` plugin emits
`/llms.txt` and `/llms-full.txt` at build time for LLM consumption.

Wiki schema and ingest/query/lint workflow live in `docs/CLAUDE.md`
(nested — automatically loaded when working under `docs/`).

## GitHub Actions

Four workflows under `.github/workflows/`:

- `test.yml` — runs pytest on Python 3.12 and 3.13 on every push and on
  PRs to `main`. Self-hosted runner. Concurrency cancels older runs.
- `docs.yml` — builds the Starlight site and deploys to GitHub Pages
  (`withastro/action@v6` + `actions/deploy-pages@v5`) on push to `main`
  touching `docs/**`.
- `release.yml` — unified release + publish pipeline on push to `main`.
  Job 1 (`release-please`, ubuntu) maintains the rolling release PR;
  job 2 (`publish`, self-hosted `python:3.12`) gates on
  `release_created == 'true'` and runs `uv build` + `uv publish` with
  PyPI trusted publishing (`id-token: write`).

Composite action `./.github/actions/setup` is the single source of
truth for the Python env setup (uv install, `.env` creation, `uv sync`).

## Version Management

**Do not bump `pyproject.toml` version manually.** Release-please owns
version state; its source of truth is
`.github/release-please-manifest.json`. On push to `main`,
release-please parses Conventional Commits since the last tag, opens
(or updates) a rolling release PR that bumps both
`.github/release-please-manifest.json` and `pyproject.toml`, and writes
`CHANGELOG.md`. Merging the release PR creates the tag and triggers
the `publish` job.

Config: `.github/release-please-config.json` (packages, release type,
visible changelog sections).
