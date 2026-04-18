---
title: ApiConfig
description: Reference for the public ApiConfig API.
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

Gathers the API access parameters (credentials, URLs, timeouts).

## See also

- [`/en/entities/api-config`](/pylegifrance/en/entities/api-config/)
