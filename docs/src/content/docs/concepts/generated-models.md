---
title: Generated models
description: Les modèles sous models/generated/ sont auto-générés depuis le schéma OpenAPI et ne doivent jamais être édités à la main.
sidebar:
  order: 5
---

Le fichier `pylegifrance/models/generated/model.py` est **auto-généré** par
[`datamodel-codegen`](https://docs.pydantic.dev/latest/integrations/datamodel_code_generator/)
à partir du schéma `pylegifrance/models/generated/legifrance.json`.

:::danger
**Ne pas éditer ce fichier à la main.** Toute modification sera écrasée à
la prochaine régénération.
:::

## Régénérer

```bash
uv run datamodel-codegen \
  --input pylegifrance/models/generated/legifrance.json \
  --output pylegifrance/models/generated/model.py
```

La config se trouve dans `pyproject.toml` sous `[tool.datamodel-codegen]`.

## Rôle dans l'architecture

- Le JSON Schema (`legifrance.json`) est la source de vérité des formes
  d'échange avec l'API.
- `model.py` offre les Pydantic v2 DTO correspondants.
- Les **modèles de domaine** (`models/<fond>/`) consomment et enveloppent
  ces DTO — voir [`/concepts/fond-facade`](/pylegifrance/concepts/fond-facade/) et
  [`/concepts/enum-wrapping`](/pylegifrance/concepts/enum-wrapping/).

## Voir aussi

- [`/concepts/architecture`](/pylegifrance/concepts/architecture/)
