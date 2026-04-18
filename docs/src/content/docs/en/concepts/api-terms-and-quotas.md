---
title: Terms, quotas and licence
description: Operational constraints imposed by the Légifrance API terms — beta status, PISTE quotas, Etalab 2.0 data licence, credential compromise.
sidebar:
  order: 8
---

Source: [PISTE Terms of Use for the Légifrance Beta API (DILA, v2)](https://piste.gouv.fr/images/cgu/DILA_Legifrance_Beta_v2.pdf)
— archived copy at `raw/legifrance/cgu-piste-legifrance-beta.pdf`. A
second Terms document (`cgu-legifrance-api-vf-15-12-2022_0.pdf`) is
published on
[legifrance.gouv.fr](https://www.legifrance.gouv.fr/contenu/pied-de-page/open-data-et-api)
but automatic download is blocked by Cloudflare; fetch manually.

## Beta status — no SLA

The API is officially **in beta** (§IV.1):

> The DILA does not guarantee any minimum availability level.

Implication for pylegifrance: expect retry-with-backoff (already done
via `tenacity` in @pylegifrance/client.py) and treat transient
outages as part of the contract.

## PISTE quotas (rate limiting)

§IV.3: PISTE applies **per-second / per-minute / per-day quotas**,
either on request count or on bandwidth. They can be global to the
application or scoped to a specific API method.

- Where to check: **PISTE → Application → Selected APIs → Actions →
  View quotas**.
- The DILA may change them at any time and will notify Users "by any
  means at the DILA's discretion" (so keep your PISTE contact email
  monitored).
- An overrun surfaces as `HTTP 429`. See
  [`/en/concepts/piste-oauth`](/pylegifrance/en/concepts/piste-oauth/)
  — pylegifrance retries on 429 via `tenacity`.

## Data licence — Etalab 2.0

§IX: data served by the API is under the
[Open Licence 2.0 (Etalab)](https://www.etalab.gouv.fr/wp-content/uploads/2017/04/ETALAB-Licence-Ouverte-v2.0.pdf).

In short:

- Free reuse, including commercial.
- Must credit the source and the last-update date of the data used.
- No misleading use that would suggest DILA certification after
  modification.

The licence applies to **the data** returned by the API, not to the
pylegifrance code (MIT — see @LICENSE).

## OAuth / PISTE credential compromise

§V.3: on suspected or confirmed compromise (abnormal consumption,
`client_secret` leaked in a public repo, etc.), the User must:

1. **Reset** credentials in PISTE immediately.
2. **Notify** the DILA and / or AIFE as soon as possible.

Pylegifrance keeps no disk persistence of tokens (see
@docs/src/content/docs/en/entities/authentication.md), which reduces
the exposure surface. Credentials stay in `.env`; never commit them.

## See also

- [`/en/concepts/piste-oauth`](/pylegifrance/en/concepts/piste-oauth/) —
  authentication flow.
- [`/en/entities/authentication`](/pylegifrance/en/entities/authentication/) —
  in-memory token handling.
- [`/en/operations/configure-api-credentials`](/pylegifrance/en/operations/configure-api-credentials/) —
  keeping credentials out of the repo.
