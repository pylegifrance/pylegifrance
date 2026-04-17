# prompts/ — Prompts LLM des demandes de fonctionnalité

Lorsqu'un·e contributeur·rice rédige une demande de fonctionnalité à l'aide d'un
LLM (ChatGPT, Claude, Codex…) et partage le prompt via le champ « Prompt LLM
utilisé » de l'issue (voir
[`.github/CONTRIBUTING.md`](../../../.github/CONTRIBUTING.md#transparence-llm-pour-les-demandes-de-fonctionnalité)),
le prompt est archivé ici.

## Convention de nommage

```
YYYY-MM-DD-issue-<n>-<slug>.md
```

Exemples :

- `2026-04-18-issue-51-cache-token-piste.md`
- `2026-05-03-issue-58-ajouter-recherche-circulaires.md`

## Format du fichier

```markdown
---
issue: 51
title: "Mettre en cache le token PISTE pour éviter les 429"
url: https://github.com/pylegifrance/pylegifrance/issues/51
author: <github-handle>
llm: claude-sonnet-4-6
submitted: 2026-04-18
---

<prompt verbatim>
```

## Rôle dans le wiki

Ces prompts sont des **sources brutes** au même titre que les docs officielles
Legifrance. Lors de l'ingestion, le LLM peut :

- repérer des concepts manquants dans `concepts/`,
- proposer de nouvelles entrées dans `references/` si l'issue cible une API,
- annoter `log.md` avec l'entrée ingérée.

Voir `../../CLAUDE.md` § 7 « Opération: Ingest ».
