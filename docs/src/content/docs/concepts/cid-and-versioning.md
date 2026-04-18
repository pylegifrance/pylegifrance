---
title: CID, consolidation et versioning
description: Comment Legifrance identifie et versionne les textes — CID, consolidation, états juridiques.
sidebar:
  order: 7
---

Ce concept est transverse à tous les fonds : il explique comment Legifrance
identifie un article (ou une section, ou un texte) à travers le temps, et
comment les modifications sont propagées.

Source : [Lexique officiel de l'API Légifrance (DILA)](https://www.legifrance.gouv.fr/contenu/Media/files/lexique-api-lgf.docx) — copie archivée dans `raw/legifrance/`.

## CID — Common Identifier

Le **CID** est l'identifiant commun à toutes les versions d'un même objet
(article, section, texte). Là où `LEGIARTI…`, `LEGITEXT…`, `LEGISCTA…`
désignent une version *précise*, le CID est le fil rouge qui relie toutes
ses versions.

- Dans **LEGI** (textes non codifiés) : le CID d'un objet créé dans LEGI est
  l'identifiant de sa **version initiale** dans JORF (p. ex. `JORFARTI…`).
  Si l'article est créé directement dans LEGI (pas de version JORF), son CID
  est lui-même un `LEGIARTI…`.
- Dans les **codes** (créés directement dans LEGI) : le CID est un
  `LEGITEXT…` / `LEGISCTA…` / `LEGIARTI…` selon le type d'objet.

## Consolidation

Quand un article est modifié, Legifrance **réécrit l'article** en intégrant
la modification — c'est le principe de consolidation. Chaque modification,
même mineure, crée une **nouvelle version** de l'article (nouveau LEGIARTI),
rattachée au même CID.

Conséquence pour pylegifrance : `fetch_version_at(text_id, date)` renvoie
la version consolidée qui était en vigueur à la date donnée ; `fetch_versions`
renvoie la liste complète des versions successives.

## États juridiques d'un article

| Code | Abréviation | Sens |
|---|---|---|
| `VIGUEUR` | V | article s'appliquant à la date courante |
| `ABROGE_DIFF` | VT | en vigueur, mais fin de vigueur déjà programmée (abrogé différé) |
| `VIGUEUR_DIFF` | VD | entrée en vigueur prévue à une date ultérieure |
| `ABROGE` | Ab | n'est plus en vigueur |
| `MODIFIE` | M | version remplacée par une version postérieure |
| `PERIME` | P | abrogation implicite (texte caduc) |
| `ANNULE` | A | annulé par le Conseil d'État |

Côté pylegifrance, ces valeurs apparaissent sur le champ
[`Article.legal_status`](/pylegifrance/entities/article/) et dans le filtre
`EtatJuridique` du builder Code (voir
[`/references/code`](/pylegifrance/references/code/)).

## Disposition « balai »

Convention spécifique à la consolidation : un texte peut remplacer en une
seule passe une expression (mots, acronymes…) dans **tous** les textes en
vigueur. Ces modifications portent sur un grand nombre de LEGIARTI à la
fois — utile à savoir si vous remarquez une vague de versions nouvelles à
la même date de signature.

## Voir aussi

- [`/entities/article`](/pylegifrance/entities/article/) — où le
  `legal_status` apparaît.
- [`/concepts/architecture`](/pylegifrance/concepts/architecture/) — où se
  place le versioning dans le flux.
