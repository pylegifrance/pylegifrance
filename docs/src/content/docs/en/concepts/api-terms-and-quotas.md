---
title: Terms, quotas and licence
description: Operational constraints imposed by the Légifrance API terms — 95% SLA, PISTE quotas, Etalab 2.0 data licence, credential compromise, CNIL/ANSSI security baseline.
sidebar:
  order: 8
---

Primary source (canonical as of April 2026):
[Légifrance API Terms of Use v1.0 — 15 Dec 2022 (DILA)](https://www.legifrance.gouv.fr/contenu/Media/files/pied-de-page/cgu-legifrance-api-vf-15-12-2022_0.pdf)
— archived copy at `raw/legifrance/cgu-legifrance-api.pdf` and its
editable `.docx` source.

Earlier version (historical, 04 Aug 2020):
[PISTE Terms of Use for the Légifrance Beta API v1.1](https://piste.gouv.fr/images/cgu/DILA_Legifrance_Beta_v2.pdf)
— copy at `raw/legifrance/cgu-piste-legifrance-beta.pdf`. Use only for
archaeology; the 2022 terms supersede it.

## Availability — 95% daily on prod (§IV.1)

The 2022 version introduces a **best-effort commitment** absent from
the 2020 one:

> The DILA targets a service commitment of 95% per day on the
> production environment provided via the PISTE service.
>
> The DILA does not target any service commitment on the sandbox
> environment.

For pylegifrance users:

- Prod → retry-with-backoff is sensible (already configured via
  `tenacity` in @pylegifrance/client.py). 5% daily downtime ≈ 72 min.
- Sandbox → no commitment; outages without prior notice.

## PISTE quotas — rate limiting (§IV.3)

PISTE applies **per-second / per-minute / per-day quotas**, either on
request count or bandwidth. They may be global to the application or
scoped to a specific API method.

- Where to check: **PISTE → "Applications" tab → the application
  consuming the API → Actions → View quotas**.
- The DILA may change them at any time and notifies "by email and /
  or by any other means at the DILA's convenience" (2022 — the 2020
  version said only "at the DILA's convenience"). Keep the PISTE
  contact email monitored.
- Overruns surface as `HTTP 429`. Pylegifrance retries via `tenacity`.

## Data licence — Etalab 2.0 (§IX)

Data served by the API is under the
[Open Licence 2.0 (Etalab)](https://www.etalab.gouv.fr/wp-content/uploads/2017/04/ETALAB-Licence-Ouverte-v2.0.pdf).
The 2022 version **explicitly includes the licence within the scope of
the Terms** (§I.1), which was implicit in 2020.

In short:

- Free reuse, including commercial.
- Must credit the source and the last-update date of the data used.
- No misleading use that would suggest DILA certification after
  modification.

The licence applies to **the data** returned by the API, not to the
pylegifrance code (MIT — see @LICENSE).

## Commercial use — at your own risk (§VI.2)

Open Licence 2.0 allows commercial reuse, **but** the DILA disclaims
liability:

> Given the lack of guarantee on data reliability (article VI.1) and
> API availability (article IV.1), such use is done at the User's own
> risk and peril.

For a commercial product depending on Légifrance: plan for a local
snapshot/cache of cited data, monitor anomaly reports, and make clear
to end users that opposable legal data lives in the Journal officiel
(signed PDFs), not the API.

## Security — CNIL / ANSSI baseline (§V.1, V.2)

The 2022 version adds that credentials must meet "in particular CNIL
and ANSSI recommendations". Expected practices (§V.2):

- Up-to-date antivirus, regular security patching, local firewall.
- Certificate-authority control.
- No password caching in the browser.
- Automatic session locking.

## OAuth / PISTE credential compromise (§V.3)

On suspected or confirmed compromise (abnormal consumption,
`client_secret` leaked in a public repo, etc.), the User must:

1. **Reset** credentials in PISTE immediately.
2. **Notify** the DILA and / or AIFE as soon as possible.

Pylegifrance keeps no disk persistence of tokens (see
@docs/src/content/docs/en/entities/authentication.md), which reduces
the exposure surface. Credentials stay in `.env`; never commit them.

## Other constraints (2022)

- **Minimum age: 15** (§I.2, "majeur numérique en France"). In 2020
  this was "adult or minor with parental consent".
- **Terms-change notifications by email** (§I.3). Keep the PISTE
  account mailbox monitored.
- **DILA GDPR contact**: `rgpd@dila.gouv.fr` — replaces the 2020
  `dpd@pm.gouv.fr`.

## See also

- [`/en/concepts/piste-oauth`](/pylegifrance/en/concepts/piste-oauth/) —
  authentication flow.
- [`/en/entities/authentication`](/pylegifrance/en/entities/authentication/) —
  in-memory token handling.
- [`/en/operations/configure-api-credentials`](/pylegifrance/en/operations/configure-api-credentials/) —
  keeping credentials out of the repo.
