---
title: PISTE OAuth
description: Flux d'authentification OAuth 2.0 client_credentials contre le portail PISTE.
sidebar:
  order: 6
---

L'API Legifrance est hébergée derrière le portail **PISTE**
(<https://piste.gouv.fr>), qui impose une authentification OAuth 2.0 en
**client credentials**.

## Flux

1. L'utilisateur·rice crée un compte PISTE et souscrit à l'API Legifrance —
   voir [`/operations/create-piste-account`](/pylegifrance/operations/create-piste-account/).
2. PISTE fournit un couple `client_id` / `client_secret`.
3. Au premier appel API, `AuthenticationManager` :
   - POST `client_id` + `client_secret` + `grant_type=client_credentials`
     + `scope=openid` (form-url-encoded) vers `token_url` (par défaut
     l'endpoint OAuth PISTE prod ; sandbox :
     `https://sandbox-oauth.piste.gouv.fr/api/oauth/token`) ;
   - reçoit un `access_token` avec une expiration (typiquement 3600 s) ;
   - attache `Authorization: Bearer <token>` aux appels suivants.

   Documentation officielle :
   [Exemples d'utilisation de l'API Légifrance (DILA)](https://www.legifrance.gouv.fr/contenu/Media/Files/pied-de-page/exemples-d-utilisation-de-l-api.docx)
   §1 — copie archivée dans `raw/legifrance/`.
4. Avant chaque `call_api` / `get`, le manager vérifie la fraîcheur du jeton
   et le rafraîchit si nécessaire.

## Deux URL, deux rôles

- `token_url` → endpoint PISTE qui délivre le jeton.
- `api_url` → base URL des endpoints Legifrance métier (recherche, consult).

Tous deux sont configurables via [`ApiConfig`](/pylegifrance/entities/api-config/) ; les
défauts visent la prod.

## En cas d'échec

- `401` à l'obtention du jeton → identifiants invalides ou abonnement API
  expiré sur PISTE.
- `429` sur les appels métier → rate limiting PISTE ; `LegifranceClient`
  utilise `tenacity` pour le retry avec back-off.

## Voir aussi

- [`/entities/authentication`](/pylegifrance/entities/authentication/)
- [`/operations/configure-api-credentials`](/pylegifrance/operations/configure-api-credentials/)
- [Guide officiel PISTE](https://piste.gouv.fr/en/help-center/guide)
