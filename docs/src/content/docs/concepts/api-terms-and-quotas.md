---
title: CGU, quotas et licence
description: Contraintes opérationnelles imposées par les CGU de l'API Légifrance — statut bêta, quotas PISTE, licence Etalab 2.0, compromission d'identifiants.
sidebar:
  order: 8
---

Source : [CGU PISTE de l'API Légifrance Beta (DILA, v2)](https://piste.gouv.fr/images/cgu/DILA_Legifrance_Beta_v2.pdf)
— copie archivée dans `raw/legifrance/cgu-piste-legifrance-beta.pdf`.
Une seconde version CGU (`cgu-legifrance-api-vf-15-12-2022_0.pdf`) est
publiée sur
[legifrance.gouv.fr](https://www.legifrance.gouv.fr/contenu/pied-de-page/open-data-et-api)
mais son téléchargement automatique est bloqué par Cloudflare ; à
récupérer manuellement.

## Statut bêta — pas de SLA

L'API est officiellement **en bêta** (§IV.1) :

> La DILA ne garantit aucun niveau minimal de disponibilité.

Conséquence pour pylegifrance : prévoir un retry-avec-backoff
(déjà fait via `tenacity` dans @pylegifrance/client.py) et accepter
que les indisponibilités transitoires fassent partie du contrat.

## Quotas PISTE (rate limiting)

§IV.3 : PISTE applique des **quotas par seconde / minute / jour**, soit
sur le nombre de requêtes, soit sur la bande passante. Ils peuvent
être globaux à l'application ou spécifiques à une méthode de l'API.

- Où les voir : **PISTE → Application → API Sélectionnées → Actions
  → Consulter les quotas**.
- La DILA peut les modifier à tout moment ; elle notifiera les
  Utilisateurs « par tout moyen à la convenance de la DILA » (donc
  surveiller le mail de contact PISTE).
- Un dépassement se manifeste côté API par un `HTTP 429`. Voir
  [`/concepts/piste-oauth`](/pylegifrance/concepts/piste-oauth/) —
  pylegifrance retry sur 429 via `tenacity`.

## Licence des données — Etalab 2.0

§IX : les données exposées par l'API sont sous
[Licence Ouverte 2.0 (Etalab)](https://www.etalab.gouv.fr/wp-content/uploads/2017/04/ETALAB-Licence-Ouverte-v2.0.pdf).

Ce que ça implique, en résumé :

- Réutilisation libre, y compris commerciale.
- Obligation de mentionner la source et la date de la dernière mise à
  jour utilisée.
- Pas d'usage trompeur qui laisserait croire que la donnée a été
  certifiée par la DILA après modification.

La licence porte sur **les données** renvoyées par l'API, pas sur le
code pylegifrance (qui est sous MIT — voir @LICENSE).

## Compromission d'identifiants OAuth / PISTE

§V.3 : en cas de compromission suspectée ou avérée (surconsommation
anormale, fuite du `client_secret` dans un repo public, etc.),
l'Utilisateur doit :

1. **Réinitialiser** ses identifiants sur PISTE immédiatement.
2. **Notifier** la DILA et / ou l'AIFE dans les plus brefs délais.

Pylegifrance n'effectue aucune persistance disque des jetons
(§« Authentication » — @docs/src/content/docs/entities/authentication.md),
ce qui réduit la surface d'exposition. Les identifiants restent dans
`.env` ; ne jamais les commiter.

## Voir aussi

- [`/concepts/piste-oauth`](/pylegifrance/concepts/piste-oauth/) — flux
  d'authentification.
- [`/entities/authentication`](/pylegifrance/entities/authentication/) —
  gestion mémoire des jetons.
- [`/operations/configure-api-credentials`](/pylegifrance/operations/configure-api-credentials/) —
  placer les identifiants en dehors du repo.
