---
title: LegifranceClient
description: HTTP client that wraps PISTE OAuth authentication and the Legifrance API calls.
sidebar:
  order: 1
---

`LegifranceClient` is the single entry point for all calls to the Legifrance
API. It wraps:

- the configuration ([`ApiConfig`](/pylegifrance/en/entities/api-config/));
- PISTE OAuth authentication ([see `concepts/piste-oauth`](/pylegifrance/en/concepts/piste-oauth/));
- a `requests.Session` with timeout management;
- the methods `call_api`, `get`, `ping`.

## Build a client

Two ways:

```python
from pylegifrance import LegifranceClient

# 1. From the environment (LEGIFRANCE_CLIENT_ID / _SECRET in .env)
client = LegifranceClient()

# 2. Manually, with an explicit ApiConfig
from pylegifrance.config import ApiConfig

client = LegifranceClient(
    ApiConfig(client_id="...", client_secret="...")
)
```

Credentials are mandatory; otherwise an error is raised at instantiation.

## Lifecycle

```python
with client.session_context():
    ...  # API calls
```

The context closes the session cleanly on exit.

## Methods

| Method | Role |
|---|---|
| `call_api(route, data)` | POST JSON to `route` |
| `get(route)` | GET to `route` |
| `ping(route="consult/ping")` | Check API reachability |
| `update_api_keys(...)` | Change credentials at runtime |

For the full signature, see [`/en/references/client`](/pylegifrance/en/references/client/).

## See also

- [`ApiConfig`](/pylegifrance/en/entities/api-config/) — shape of the config passed to the client.
- [`Authentication`](/pylegifrance/en/entities/authentication/) — what happens before every call.
- [`Fond Code`](/pylegifrance/en/entities/fond-code/), [`Fond Juri`](/pylegifrance/en/entities/fond-juri/),
  [`Fond LODA`](/pylegifrance/en/entities/fond-loda/) — facades that consume the client.
