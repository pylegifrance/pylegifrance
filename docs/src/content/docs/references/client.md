---
title: LegifranceClient
description: Référence de l'API publique de LegifranceClient.
sidebar:
  order: 1
---

```python
class LegifranceClient:
    def __init__(self, config: ApiConfig | None = None)

    @classmethod
    def create(cls, config: ApiConfig | None = None) -> Self

    def update_api_keys(
        self,
        legifrance_api_key: str | None = None,
        legifrance_api_secret: str | None = None,
    )

    def call_api(self, route: str, data: Any) -> requests.Response
    def get(self, route: str) -> requests.Response
    def ping(self, route: str = "consult/ping") -> bool
    def session_context(self)  # contextmanager
    def close(self) -> None
```

Gère l'authentification OAuth PISTE et les appels à l'API Legifrance.

## Voir aussi

- [`/entities/legifrance-client`](/pylegifrance/entities/legifrance-client/)
- [`/references/config`](/pylegifrance/references/config/)
