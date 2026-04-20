---
title: Fond KALI
description: Facade to consult and search French national collective bargaining agreements (KALI).
sidebar:
  order: 7
sources:
  - "@docs/raw/legifrance/description-des-tris-et-filtres-de-l-api.md"
  - "@docs/raw/legifrance/exemples-d-utilisation-de-l-api.md"
related:
  - /en/concepts/fond-facade
  - /en/entities/fond-code
  - /en/entities/fond-juri
updated: 2026-04-20
---

The `KaliAPI` class (in `pylegifrance/fonds/kali.py`) is the facade that
exposes the endpoints of the **KALI** fond: French national collective
bargaining agreements, along with their side agreements and amendments.

## Scope

KALI organises collective agreements on two levels:

- a **container** (`KALICONT...`), identified by an IDCC number, which
  groups a collective agreement as a whole;
- **texts** (`KALITEXT...`) — base text, amendments, side agreements —
  which are the actually consultable units, along with their sections
  (`KALISCTA...`) and articles (`KALIARTI...`).

KALI does not expose a `/version` or `/versions` endpoint, so there is
no equivalent to `.at(date)` or `.versions()` like on the LODA fond.

## Usage

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.kali import KaliAPI
from pylegifrance.models.kali.search import SearchRequest
from pylegifrance.models.kali.enum import TypeChampKali, SortKali

client = LegifranceClient(client_id="...", client_secret="...")
kali = KaliAPI(client)

# Agreement by IDCC number
ccn = kali.fetch_by_idcc("1261")
print(ccn.titre, ccn.texte_base_ids)

# Agreement by KALICONT identifier
ccn = kali.fetch_container("KALICONT000005635384")

# Text (base, amendment…) by KALITEXT identifier
texte = kali.fetch_text("KALITEXT000005677408")

# Single prefix-based dispatcher
obj = kali.fetch("KALIARTI000005833238")  # -> TexteKali (kaliArticle endpoint)

# Free-text search (hydrated into ConventionCollective objects)
results = kali.search("santé prévoyance")

# Structured search
req = SearchRequest(
    search="2098",
    field=TypeChampKali.IDCC,
    idcc="2098",
    sort=SortKali.SIGNATURE_DATE_DESC,
)
results = kali.search(req)
```

## Exposed components

- `KaliAPI.fetch_container(id)` → `ConventionCollective` (`POST /consult/kaliCont`).
- `KaliAPI.fetch_by_idcc(idcc)` → `ConventionCollective` (`POST /consult/kaliContIdcc`).
- `KaliAPI.fetch_text(id)` → `TexteKali` (`POST /consult/kaliText`).
- `KaliAPI.fetch_article(id)` → parent `TexteKali` (`POST /consult/kaliArticle`).
- `KaliAPI.fetch_section(id)` → parent `TexteKali` (`POST /consult/kaliSection`).
- `KaliAPI.fetch(id)` → prefix-based dispatcher (`KALICONT` / `KALITEXT` /
  `KALIARTI` / `KALISCTA`).
- `KaliAPI.search(query)` → `list[ConventionCollective]` via `POST /search`
  with `fond: "KALI"`.

## Search model

`SearchRequest` (in `pylegifrance/models/kali/search.py`) produces a
`SearchRequestDTO` in the format expected by the `/search` endpoint.
Supported fields:

| Field | Usage |
|---|---|
| `search` | Free text |
| `field` | `ALL`, `TITLE`, `IDCC`, `MOTS_CLES`, `ARTICLE` |
| `search_type` | `EXACTE`, `TOUS_LES_MOTS_DANS_UN_CHAMP`… |
| `sort` | `PERTINENCE`, `SIGNATURE_DATE_DESC`/`_ASC`, `MODIFICATION_DATE_DESC` |
| `idcc` | IDCC filter (`IDCC` facet) |
| `legal_status` | Legal status filter (`LEGAL_STATUS` facet) — see below |
| `date_signature_start` / `date_signature_end` | Signature date range (`DATE_SIGNATURE` facet) |

By default, `legal_status` is pre-filled with
`["VIGUEUR", "VIGUEUR_ETEN", "VIGUEUR_NON_ETEN"]`: only agreements
**currently in force** (extended or not) come back. Passing
`legal_status=None` or `legal_status=[]` disables this filter and also
returns repealed or expired texts.

Other documented facets (`ACTIVITE`, `NUM_TEXTE_CITE`, `NOM_CODE_CITE`…)
are not wired yet — to be added on demand.

## See also

- [Fond facade](/pylegifrance/en/concepts/fond-facade/) — why facades and
  models are kept separate.
- Official raw: `docs/raw/legifrance/description-des-tris-et-filtres-de-l-api.md`
  (KALI section and `consult-kali*`).

:::caution
It is the user's sole responsibility to verify that the information returned
by the API is relevant and up to date.
:::
