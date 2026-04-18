---
title: ApiConfig
description: Legifrance API access configuration — PISTE credentials, URLs, timeouts.
sidebar:
  order: 2
---

`ApiConfig` gathers the parameters needed to reach the Legifrance API. It is
consumed by [`LegifranceClient`](/pylegifrance/en/entities/legifrance-client/).

## Fields

| Field | Type | Default | Role |
|---|---|---|---|
| `client_id` | `str` | — | PISTE identifier (required) |
| `client_secret` | `str` | — | PISTE secret (required) |
| `token_url` | `str` | PISTE prod | OAuth endpoint |
| `api_url` | `str` | Legifrance prod | REST base URL |
| `connect_timeout` | `float` | `3.05` | connect timeout (s) |
| `read_timeout` | `float` | `27.0` | read timeout (s) |

## Build a config

```python
from pylegifrance.config import ApiConfig

# Manual
config = ApiConfig(client_id="...", client_secret="...")

# From the environment (LEGIFRANCE_CLIENT_ID / _SECRET)
config = ApiConfig.from_env()
```

`from_env()` loads `.env` via `python-dotenv`; see
[`/en/operations/configure-api-credentials`](/pylegifrance/en/operations/configure-api-credentials/).

## See also

- [`/en/concepts/piste-oauth`](/pylegifrance/en/concepts/piste-oauth/) — why
  `token_url` and `api_url` are distinct.
- [`/en/references/config`](/pylegifrance/en/references/config/) — signatures.
