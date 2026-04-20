---
title: Fond KALI
description: Façade pour consulter et rechercher les conventions collectives nationales (KALI).
sidebar:
  order: 6
sources:
  - "@docs/raw/legifrance/description-des-tris-et-filtres-de-l-api.md"
  - "@docs/raw/legifrance/exemples-d-utilisation-de-l-api.md"
related:
  - /concepts/fond-facade
  - /entities/fond-code
  - /entities/fond-juri
updated: 2026-04-20
---

La classe `KaliAPI` (dans `pylegifrance/fonds/kali.py`) est la façade qui
expose les endpoints du fond **KALI** : les conventions collectives
nationales étendues, leurs accords et avenants.

## Portée

Le fond KALI organise les conventions collectives sur deux niveaux :

- un **conteneur** (`KALICONT...`), identifié par un numéro IDCC, qui
  regroupe une convention collective dans son ensemble ;
- des **textes** (`KALITEXT...`) — texte de base, avenants, accords —
  qui sont les unités réellement consultables, avec leurs sections
  (`KALISCTA...`) et articles (`KALIARTI...`).

KALI n'expose pas d'endpoint `/version` ni `/versions` : il n'y a donc
pas d'équivalent à `.at(date)` ou `.versions()` comme sur le fond LODA.

## Usage

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.kali import KaliAPI
from pylegifrance.models.kali.search import SearchRequest
from pylegifrance.models.kali.enum import TypeChampKali, SortKali

client = LegifranceClient(client_id="...", client_secret="...")
kali = KaliAPI(client)

# Convention par numéro IDCC
ccn = kali.fetch_by_idcc("1261")
print(ccn.titre, ccn.texte_base_ids)

# Convention par identifiant KALICONT
ccn = kali.fetch_container("KALICONT000005635384")

# Texte (base, avenant...) par identifiant KALITEXT
texte = kali.fetch_text("KALITEXT000005677408")

# Dispatcher unique basé sur le préfixe
obj = kali.fetch("KALIARTI000005833238")  # -> TexteKali (endpoint kaliArticle)

# Recherche libre (hydratée vers des ConventionCollective)
resultats = kali.search("santé prévoyance")

# Recherche structurée
req = SearchRequest(
    search="2098",
    field=TypeChampKali.IDCC,
    idcc="2098",
    sort=SortKali.SIGNATURE_DATE_DESC,
)
resultats = kali.search(req)
```

## Composants exposés

- `KaliAPI.fetch_container(id)` → `ConventionCollective` (`POST /consult/kaliCont`).
- `KaliAPI.fetch_by_idcc(idcc)` → `ConventionCollective` (`POST /consult/kaliContIdcc`).
- `KaliAPI.fetch_text(id)` → `TexteKali` (`POST /consult/kaliText`).
- `KaliAPI.fetch_article(id)` → `TexteKali` parent (`POST /consult/kaliArticle`).
- `KaliAPI.fetch_section(id)` → `TexteKali` parent (`POST /consult/kaliSection`).
- `KaliAPI.fetch(id)` → dispatcher par préfixe (`KALICONT` / `KALITEXT` /
  `KALIARTI` / `KALISCTA`).
- `KaliAPI.search(query)` → `list[ConventionCollective]` via `POST /search`
  avec `fond: "KALI"`.

## Modèle de recherche

`SearchRequest` (dans `pylegifrance/models/kali/search.py`) génère un
`SearchRequestDTO` au format attendu par l'endpoint `/search`. Champs
pris en charge :

| Champ | Utilisation |
|---|---|
| `search` | Texte libre |
| `field` | `ALL`, `TITLE`, `IDCC`, `MOTS_CLES`, `ARTICLE` |
| `search_type` | `EXACTE`, `TOUS_LES_MOTS_DANS_UN_CHAMP`… |
| `sort` | `PERTINENCE`, `SIGNATURE_DATE_DESC`/`_ASC`, `MODIFICATION_DATE_DESC` |
| `idcc` | Filtre IDCC (facette `IDCC`) |
| `legal_status` | Filtre état juridique (facette `LEGAL_STATUS`) — voir ci-dessous |
| `date_signature_start` / `date_signature_end` | Plage date de signature (facette `DATE_SIGNATURE`) |

Par défaut, `legal_status` est pré-rempli à
`["VIGUEUR", "VIGUEUR_ETEN", "VIGUEUR_NON_ETEN"]` : seules les
conventions **en vigueur** (étendues ou non) remontent. Passer
`legal_status=None` ou `legal_status=[]` désactive ce filtre et
retourne également les textes abrogés / périmés.

Les autres facettes documentées (`ACTIVITE`, `NUM_TEXTE_CITE`,
`NOM_CODE_CITE`…) n'ont pas été câblées — à ajouter à la demande.

## Voir aussi

- [Fond facade](/pylegifrance/concepts/fond-facade/) — pourquoi les
  façades et les modèles sont séparés.
- Raw officiel : `docs/raw/legifrance/description-des-tris-et-filtres-de-l-api.md`
  (section KALI et `consult-kali*`).

:::caution
Il est de la responsabilité exclusive de l'utilisateur·rice de vérifier
que les informations renvoyées par l'API sont pertinentes et à jour.
:::
