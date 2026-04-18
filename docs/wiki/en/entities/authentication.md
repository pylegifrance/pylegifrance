---
title: Authentication
description: PISTE OAuth token management — refreshed automatically before every call.
sidebar:
  order: 3
---

The `pylegifrance/auth.py` module wraps the logic for obtaining and
refreshing PISTE OAuth tokens. It is used internally by
[`LegifranceClient`](/pylegifrance/en/entities/legifrance-client/); users
don't need to instantiate it directly.

## Behavior

- An `AuthenticationManager` is created alongside the client.
- Before each `call_api` or `get`, the manager checks token freshness and
  refreshes it against `token_url` when needed.
- Tokens are kept in memory (no disk persistence).

## Source of truth

The flow is documented in
[`/en/concepts/piste-oauth`](/pylegifrance/en/concepts/piste-oauth/).

## See also

- [`ApiConfig`](/pylegifrance/en/entities/api-config/) — provides `client_id`,
  `client_secret`, `token_url`.
- [`LegifranceClient`](/pylegifrance/en/entities/legifrance-client/) — primary
  consumer.
