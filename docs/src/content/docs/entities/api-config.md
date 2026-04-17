---
title: ApiConfig
description: Configuration d'accès à l'API Legifrance — identifiants PISTE, URL, timeouts.
sidebar:
  order: 2
---

`ApiConfig` regroupe les paramètres nécessaires pour joindre l'API Legifrance.
Il est consommé par [`LegifranceClient`](/pylegifrance/entities/legifrance-client/).

## Champs

| Champ | Type | Défaut | Rôle |
|---|---|---|---|
| `client_id` | `str` | — | identifiant PISTE (obligatoire) |
| `client_secret` | `str` | — | secret PISTE (obligatoire) |
| `token_url` | `str` | PISTE prod | endpoint OAuth |
| `api_url` | `str` | Legifrance prod | base URL REST |
| `connect_timeout` | `float` | `3.05` | timeout de connexion (s) |
| `read_timeout` | `float` | `27.0` | timeout de lecture (s) |

## Construire une config

```python
from pylegifrance.config import ApiConfig

# Manuel
config = ApiConfig(client_id="...", client_secret="...")

# Depuis l'environnement (LEGIFRANCE_CLIENT_ID / _SECRET)
config = ApiConfig.from_env()
```

`from_env()` lit `.env` via `python-dotenv` ; voir
[`/operations/configure-api-credentials`](/pylegifrance/operations/configure-api-credentials/).

## Voir aussi

- [`/concepts/piste-oauth`](/pylegifrance/concepts/piste-oauth/) — pourquoi `token_url` et
  `api_url` sont distincts.
- [`/references/config`](/pylegifrance/references/config/) — signatures.
