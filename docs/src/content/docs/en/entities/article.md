---
title: Article
description: Domain model representing a legal article (LEGIARTI) returned by the API.
sidebar:
  order: 7
---

An **article** is a textual unit inside a code or a LODA text, identified by
a LEGIARTI. On the domain side, facades return `Article` objects (a Pydantic
v2 model defined in `pylegifrance/models/code/models.py`).

## Main fields

| Field | Type | Role |
|---|---|---|
| `id` | `str` | LEGIARTI, unique identifier |
| `number` | `str` | official number (`"L36-11"`, `"1382"`) |
| `title` | `str \| None` | label |
| `content` | `str` | raw text |
| `content_html` | `str \| None` | formatted HTML text |
| `cid` | `str \| None` | parent code LEGITEXT |
| `code_name` | `str \| None` | code name (`"Code civil"`) |
| `version_date` | `datetime \| None` | version date (auto-parsed from Unix timestamp or ISO) |
| `legal_status` | `str \| None` | legal status — see [`/en/concepts/cid-and-versioning`](/pylegifrance/en/concepts/cid-and-versioning/) for the full list (`VIGUEUR`, `VIGUEUR_AVEC_TERME`, `VIGUEUR_DIFFEREE`, `ABROGE`, …) |
| `url` | `str \| None` | legifrance.gouv.fr URL |

Useful method: `article.format_citation()` →
`"Code civil, art. 1 (version du 01/01/2020)"`.

## Direct fetch

Via [`Fond Code`](/pylegifrance/en/entities/fond-code/):

```python
fetcher = code.fetch_article("LEGIARTI000006419305")
article = fetcher.at("2022-01-01")   # version at a date
```

## Legifrance terminology

| Identifier | Role |
|---|---|
| `LEGITEXT…` | identifier of a code or a LODA text |
| `LEGIARTI…` | identifier of an article |
| `JURITEXT…` | identifier of a case law decision |

See the official Legifrance glossary in
[Official Légifrance API glossary (DILA)](https://www.legifrance.gouv.fr/contenu/Media/files/lexique-api-lgf.docx).

## See also

- [`/en/concepts/generated-models`](/pylegifrance/en/concepts/generated-models/) —
  where the raw shape comes from.
- [`/en/entities/fond-code`](/pylegifrance/en/entities/fond-code/) — facade
  that produces articles.
