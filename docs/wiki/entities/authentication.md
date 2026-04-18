---
title: Authentication
description: Gestion des jetons OAuth PISTE, rafraîchis automatiquement avant chaque appel.
sidebar:
  order: 3
---

Le module `pylegifrance/auth.py` encapsule la logique d'obtention et de
rafraîchissement des jetons OAuth PISTE. Il est utilisé en interne par
[`LegifranceClient`](/pylegifrance/entities/legifrance-client/) ; l'utilisateur·rice n'a
pas besoin de l'instancier directement.

## Comportement

- Un `AuthenticationManager` est créé au côté du client.
- Avant chaque `call_api` ou `get`, le manager vérifie la fraîcheur du jeton
  et le renouvelle si nécessaire auprès de `token_url`.
- Les jetons sont tenus en mémoire (pas de persistance sur disque).

## Source de vérité

Le flux est documenté dans [`/concepts/piste-oauth`](/pylegifrance/concepts/piste-oauth/).

## Voir aussi

- [`ApiConfig`](/pylegifrance/entities/api-config/) — fournit `client_id`, `client_secret`,
  `token_url`.
- [`LegifranceClient`](/pylegifrance/entities/legifrance-client/) — consommateur principal.
