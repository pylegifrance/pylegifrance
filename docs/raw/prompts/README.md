# prompts/ — Prompts LLM des Pull Requests

Lorsqu'un·e contributeur·rice rédige une Pull Request à l'aide d'un LLM
(ChatGPT, Claude, Codex…) et partage le prompt via la section « Prompt
LLM utilisé » du modèle de PR (voir @.github/CONTRIBUTING.md, section
« Transparence LLM pour les PR »), le prompt est archivé ici.

> ℹ️ Les issues GitHub sont désactivées sur ce repo : la collecte des
> prompts se fait exclusivement via les PR.

## Convention de nommage

```
YYYY-MM-DD-pr-<n>-<slug>.md
```

Exemples :

- `2026-04-18-pr-51-cache-token-piste.md`
- `2026-05-03-pr-58-ajouter-recherche-circulaires.md`

## Format du fichier

```markdown
---
pr: 51
title: "Mettre en cache le token PISTE pour éviter les 429"
url: https://github.com/pylegifrance/pylegifrance/pull/51
author: <github-handle>
llm: claude-sonnet-4-6
submitted: 2026-04-18
---

<prompt verbatim>
```

## Rôle dans le wiki

Ces prompts sont des **sources brutes** au même titre que les docs
officielles Legifrance. Lors de l'ingestion, le LLM peut :

- repérer des concepts manquants dans `concepts/`,
- proposer de nouvelles entrées dans `references/` si la PR cible une
  API,
- annoter `log.md` avec l'entrée ingérée.

Voir @docs/CLAUDE.md § 7 « Opération: Ingest ».
