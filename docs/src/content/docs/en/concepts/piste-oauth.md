---
title: PISTE OAuth
description: OAuth 2.0 client_credentials authentication flow against the PISTE portal.
sidebar:
  order: 6
---

The Legifrance API is hosted behind the **PISTE** portal
(<https://piste.gouv.fr>), which requires OAuth 2.0 authentication in
**client credentials** mode.

## Flow

1. The user creates a PISTE account and subscribes to the Legifrance API —
   see [`/en/operations/create-piste-account`](/pylegifrance/en/operations/create-piste-account/).
2. PISTE returns a `client_id` / `client_secret` pair.
3. On the first API call, `AuthenticationManager`:
   - POSTs `client_id` + `client_secret` + `grant_type=client_credentials`
     + `scope=openid` (form-url-encoded) to `token_url` (the PISTE prod
     OAuth endpoint by default; sandbox:
     `https://sandbox-oauth.piste.gouv.fr/api/oauth/token`);
   - receives an `access_token` with an expiration (typically 3600 s);
   - attaches `Authorization: Bearer <token>` to subsequent calls.

   Official reference:
   [Légifrance API usage examples (DILA)](https://www.legifrance.gouv.fr/contenu/Media/Files/pied-de-page/exemples-d-utilisation-de-l-api.docx)
   §1 — archived copy in `raw/legifrance/`.
4. Before every `call_api` / `get`, the manager checks token freshness and
   refreshes it when needed.

## Two URLs, two roles

- `token_url` → PISTE endpoint that issues the token.
- `api_url` → base URL of the Legifrance business endpoints (search, consult).

Both are configurable via [`ApiConfig`](/pylegifrance/en/entities/api-config/);
defaults point at prod.

## On failure

- `401` on token request → invalid credentials or expired API subscription
  on PISTE.
- `429` on business calls → PISTE rate limiting; `LegifranceClient` uses
  `tenacity` for retry with back-off.

## See also

- [`/en/entities/authentication`](/pylegifrance/en/entities/authentication/)
- [`/en/operations/configure-api-credentials`](/pylegifrance/en/operations/configure-api-credentials/)
- [Official PISTE guide](https://piste.gouv.fr/en/help-center/guide)
