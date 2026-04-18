---
title: Configure API credentials
description: Two ways to pass PISTE credentials to the client.
sidebar:
  order: 4
---

Two options — environment variables (recommended) or a manual
`ApiConfig`.

## 1. Environment variables (`.env`)

Create a `.env` file at the project root:

```bash
LEGIFRANCE_CLIENT_ID=your_client_id
LEGIFRANCE_CLIENT_SECRET=your_client_secret
```

Then:

```python
from pylegifrance import LegifranceClient

client = LegifranceClient()    # reads .env via python-dotenv
```

:::caution
`.env` must stay **out of git** (`.gitignore`). Never log
`client_secret`.
:::

## 2. Manual configuration

Useful when keys come from a vault or an external system:

```python
from pylegifrance import LegifranceClient
from pylegifrance.config import ApiConfig

client = LegifranceClient(
    ApiConfig(client_id="...", client_secret="...")
)
```

Credentials are **mandatory** at instantiation; otherwise an error is
raised.

## See also

- [`/en/entities/api-config`](/pylegifrance/en/entities/api-config/)
- [`/en/concepts/piste-oauth`](/pylegifrance/en/concepts/piste-oauth/)
