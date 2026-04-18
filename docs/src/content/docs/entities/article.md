---
title: Article
description: Modèle de domaine représentant un article juridique (LEGIARTI) renvoyé par l'API.
sidebar:
  order: 7
---

Un **article** désigne une unité textuelle dans un code ou un texte LODA,
identifiée par un LEGIARTI. Côté domaine, les façades renvoient des objets
`Article` (modèle Pydantic v2, défini dans
`pylegifrance/models/code/models.py`).

## Champs principaux

| Champ | Type | Rôle |
|---|---|---|
| `id` | `str` | LEGIARTI, identifiant unique |
| `number` | `str` | numéro officiel (`"L36-11"`, `"1382"`) |
| `title` | `str \| None` | intitulé |
| `content` | `str` | texte brut |
| `content_html` | `str \| None` | texte HTML formaté |
| `cid` | `str \| None` | LEGITEXT du code parent |
| `code_name` | `str \| None` | nom du code (`"Code civil"`) |
| `version_date` | `datetime \| None` | date de version (auto-parsée depuis timestamp Unix ou ISO) |
| `legal_status` | `str \| None` | état juridique — voir [`/concepts/cid-and-versioning`](/pylegifrance/concepts/cid-and-versioning/) pour la liste complète (`VIGUEUR`, `VIGUEUR_AVEC_TERME`, `VIGUEUR_DIFFEREE`, `ABROGE`, …) |
| `url` | `str \| None` | URL sur legifrance.gouv.fr |

Méthode utile : `article.format_citation()` →
`"Code civil, art. 1 (version du 01/01/2020)"`.

## Récupération directe

Via [`Fond Code`](/pylegifrance/entities/fond-code/) :

```python
fetcher = code.fetch_article("LEGIARTI000006419305")
article = fetcher.at("2022-01-01")   # version à une date
```

## Terminologie Legifrance

| Identifiant | Rôle |
|---|---|
| `LEGITEXT…` | identifiant d'un code ou d'un texte LODA |
| `LEGIARTI…` | identifiant d'un article |
| `JURITEXT…` | identifiant d'une décision de jurisprudence |

Voir le lexique Legifrance officiel dans
[Lexique officiel de l'API Légifrance (DILA)](https://www.legifrance.gouv.fr/contenu/Media/files/lexique-api-lgf.docx).

## Voir aussi

- [`/concepts/generated-models`](/pylegifrance/concepts/generated-models/) — d'où vient la
  forme brute.
- [`/entities/fond-code`](/pylegifrance/entities/fond-code/) — façade qui produit des
  articles.
