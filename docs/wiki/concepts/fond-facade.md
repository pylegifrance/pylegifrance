---
title: Fond facade
description: Pattern de façade par fond documentaire (Code, Juri, LODA) pour isoler l'API publique des DTO générés.
sidebar:
  order: 3
---

Chaque **fond** Legifrance (Code, Juri, LODA, JORF…) a sa propre façade dans
`pylegifrance/fonds/`. Une façade :

1. prend un [`LegifranceClient`](/pylegifrance/entities/legifrance-client/) (et un
   paramètre `fond` optionnel pour sélectionner la base — ex. `CODE_DATE` vs
   `CODE_ETAT`) ;
2. expose `.search()` qui retourne un **builder** fluide
   ([voir `/concepts/builder-pattern`](/pylegifrance/concepts/builder-pattern/)) ;
3. expose des `.fetch_*()` qui retournent des **fetchers** (pattern builder
   plus focalisé).

## Invariant de conception

> Tout ce qui n'est pas `pylegifrance/fonds/*` ni `pylegifrance/__init__.py`
> est considéré comme **interne**.

Les utilisateur·rice·s n'instancient jamais directement les modèles sous
`models/generated/` — ils·elles passent toujours par la façade, qui compose
les modèles de domaine (`models/<fond>/`) puis les convertit en DTO générés
(`to_generated()`) avant l'appel API.

## Bénéfices

- **Stabilité publique** : le schéma OpenAPI de Legifrance peut changer sans
  casser l'API pylegifrance.
- **Ergonomie** : la façade offre des raccourcis (ex. `search("mot")` pour
  les cas simples).
- **Enrichissement** : les objets retournés par la façade ont des méthodes
  métier (ex. `decision.at(date)`) absentes du DTO brut.

## Voir aussi

- [`/concepts/architecture`](/pylegifrance/concepts/architecture/)
- [`/concepts/enum-wrapping`](/pylegifrance/concepts/enum-wrapping/)
