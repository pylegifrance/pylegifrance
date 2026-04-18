---
title: CID, consolidation and versioning
description: How Legifrance identifies and versions texts — CID, consolidation, legal statuses.
sidebar:
  order: 7
---

This concept is transverse to every fond: it explains how Legifrance
identifies an article (or a section, or a text) across time, and how
modifications propagate.

Source: [Official Légifrance API glossary (DILA)](https://www.legifrance.gouv.fr/contenu/Media/files/lexique-api-lgf.docx) — archived copy in `raw/legifrance/`.

## CID — Common Identifier

The **CID** is the identifier shared by every version of the same object
(article, section, text). Where `LEGIARTI…`, `LEGITEXT…`, `LEGISCTA…`
designate one *specific* version, the CID is the thread that links all
versions together.

- In **LEGI** (non-codified texts): the CID of an object created in LEGI is
  the identifier of its **initial version** in JORF (e.g. `JORFARTI…`).
  If the article was created directly in LEGI (no JORF version), its CID is
  itself a `LEGIARTI…`.
- In **codes** (created directly in LEGI): the CID is a `LEGITEXT…` /
  `LEGISCTA…` / `LEGIARTI…` depending on the object type.

## Consolidation

When an article is modified, Legifrance **rewrites the article** inlining
the change — this is the consolidation principle. Every modification, even
minor, creates a **new version** of the article (new LEGIARTI), attached to
the same CID.

Consequence for pylegifrance: `fetch_version_at(text_id, date)` returns the
consolidated version that was in force at the given date;
`fetch_versions` returns the full list of successive versions.

## Article legal statuses

| Code | Abbreviation | Meaning |
|---|---|---|
| `VIGUEUR` | V | article in force as of today |
| `VIGUEUR_AVEC_TERME` | VT | in force, but its end date is already scheduled (sometimes called "deferred abrogation") |
| `VIGUEUR_DIFFEREE` | VD | entry into force scheduled for a later date |
| `ABROGE` | Ab | no longer in force |
| `ABROGE_DIFF` | — | scheduled abrogation (variant of VT) |
| `MODIFIE` | — | version superseded by a later one |

On the pylegifrance side, these values appear on the
[`Article.legal_status`](/pylegifrance/en/entities/article/) field and on
the Code builder's `EtatJuridique` filter (see
[`/en/references/code`](/pylegifrance/en/references/code/)).

## "Sweep" provisions (dispositions balai)

A consolidation-specific convention: a text may replace an expression
(words, acronyms…) in **every** in-force text in a single pass. Such
changes touch a large number of LEGIARTIs at once — useful to know if you
notice a surge of new versions with the same signature date.

## See also

- [`/en/entities/article`](/pylegifrance/en/entities/article/) — where
  `legal_status` is exposed.
- [`/en/concepts/architecture`](/pylegifrance/en/concepts/architecture/) —
  where versioning fits in the flow.
