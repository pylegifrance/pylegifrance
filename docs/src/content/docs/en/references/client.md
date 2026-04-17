---
title: LegifranceClient
description: Reference for the public LegifranceClient API.
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

Handles PISTE OAuth authentication and calls to the Legifrance API.

## See also

- [`/en/entities/legifrance-client`](/pylegifrance/en/entities/legifrance-client/)
- [`/en/references/config`](/pylegifrance/en/references/config/)
