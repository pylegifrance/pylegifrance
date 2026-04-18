# Contribuer à pylegifrance

> Les issues GitHub sont désactivées. Ouvrez directement une Pull Request.

## Mise en place

```bash
uv sync --all-extras
uv run pre-commit install   # installe les hooks pre-commit et commit-msg
```

## Workflow

```bash
# 1. Branche depuis main à jour
git switch main && git pull --ff-only
git switch -c <type>/<slug>   # ex : feat/cache-token

# 2. Commits Conventional Commits
# Types : feat, fix, perf, refactor, docs, ci, chore, test, build, style, revert
# Le hook commit-msg valide le format localement.

# 3. PR
git push -u origin <branche>
gh pr create   # sans --fill pour laisser le modèle se charger
```

## Transparence LLM

Si vous avez utilisé un LLM pour rédiger votre contribution, collez le prompt verbatim dans la section « Prompt LLM utilisé » du modèle de PR. Ces prompts alimentent le wiki (`docs/raw/prompts/`).

## Standards de codage

Appliqués automatiquement par ruff et ty au commit. Pour les conventions qui ne se vérifient pas automatiquement (architecture, patterns Pydantic, tests BDD), voir [`.claude/rules/`](../.claude/rules/).
