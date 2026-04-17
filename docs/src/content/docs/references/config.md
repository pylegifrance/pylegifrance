---
title: ApiConfig
description: Référence de l'API publique d'ApiConfig.
sidebar:
  order: 2
---

```python
class ApiConfig:
    def __init__(
        client_id: str,
        client_secret: str,
        token_url: str = "...",
        api_url: str = "...",
        connect_timeout: float = 3.05,
        read_timeout: float = 27.0,
    )

    @classmethod
    def from_env() -> "ApiConfig"
```

Regroupe les paramètres d'accès à l'API (identifiants, URL, timeouts).

## Voir aussi

- [`/entities/api-config`](/pylegifrance/entities/api-config/)
