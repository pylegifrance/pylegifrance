---
title: CGU, quotas et licence
description: Contraintes opérationnelles imposées par les CGU de l'API Légifrance — SLA 95%, quotas PISTE, licence Etalab 2.0, compromission d'identifiants, sécurité CNIL/ANSSI.
sidebar:
  order: 8
---

Source principale (canonique en avril 2026) :
[CGU API Légifrance v1.0 — 15/12/2022 (DILA)](https://www.legifrance.gouv.fr/contenu/Media/files/pied-de-page/cgu-legifrance-api-vf-15-12-2022_0.pdf)
— copie archivée dans `raw/legifrance/cgu-legifrance-api.pdf` (et sa
version éditable `.docx`).

Source antérieure (historique, 04/08/2020) :
[CGU PISTE de l'API Légifrance Beta v1.1](https://piste.gouv.fr/images/cgu/DILA_Legifrance_Beta_v2.pdf)
— copie dans `raw/legifrance/cgu-piste-legifrance-beta.pdf`. À utiliser
uniquement pour archéologie ; les CGU 2022 prévalent.

## Disponibilité — 95 % par jour sur prod (§IV.1)

La v2022 introduit un **engagement de moyens** absent de la version
2020 :

> La DILA vise un engagement de service de 95 % par jour sur
> l'environnement de production mis à disposition via le service PISTE.
>
> La DILA ne vise pas d'engagement de service sur l'environnement de
> sandbox.

Concrètement pour pylegifrance :

- Prod → retry-avec-backoff raisonnable (déjà fait via `tenacity` dans
  @pylegifrance/client.py). 5 % de downtime quotidien = ~72 min.
- Sandbox → aucun engagement, indisponibilités sans préavis.

## Quotas PISTE — rate limiting (§IV.3)

PISTE applique des **quotas par seconde / minute / jour**, soit sur le
nombre de requêtes, soit sur la bande passante. Globaux à l'application
ou spécifiques à une méthode.

- Où les voir : **PISTE → onglet « Applications » → application
  consommant l'API → Actions → Consulter les quotas**.
- La DILA peut les modifier à tout moment et notifie « par email
  et / ou par tout autre moyen à la convenance de la DILA » (v2022 —
  la v2020 disait seulement « à la convenance de la DILA »). Garder
  l'email PISTE à jour.
- Un dépassement se manifeste par `HTTP 429`. Pylegifrance retry via
  `tenacity`.

## Licence des données — Etalab 2.0 (§IX)

Les données exposées par l'API sont sous
[Licence Ouverte 2.0 (Etalab)](https://www.etalab.gouv.fr/wp-content/uploads/2017/04/ETALAB-Licence-Ouverte-v2.0.pdf).
La v2022 **inclut explicitement la licence dans le périmètre des CGU**
(I.1), ce qui était implicite en 2020.

Résumé :

- Réutilisation libre, y compris commerciale.
- Obligation de mentionner la source et la date de la dernière mise à
  jour utilisée.
- Pas d'usage trompeur qui laisserait croire que la donnée a été
  certifiée par la DILA après modification.

La licence porte sur **les données** renvoyées par l'API, pas sur le
code pylegifrance (qui est sous MIT — voir @LICENSE).

## Usage commercial — à vos risques et périls (§VI.2)

La Licence 2.0 autorise l'usage commercial, **mais** la DILA décline
toute responsabilité :

> Compte tenu de l'absence de garantie de fiabilité de ces données
> (article VI.1) et de disponibilité de l'API (article IV.1), un tel
> usage se fait au risque et péril de l'Utilisateur.

Pour un produit commercial qui dépend de Légifrance : prévoir un
snapshot/cache local des données citées, monitorer les anomalies
signalées, et afficher clairement à l'utilisateur final que les données
juridiques opposables sont celles du Journal officiel (PDF signés),
pas celles de l'API.

## Sécurité — baseline CNIL / ANSSI (§V.1, V.2)

La v2022 ajoute que les identifiants doivent respecter « en
particulier les recommandations de la CNIL et de l'ANSSI ». Pratiques
attendues (§V.2) :

- Antivirus à jour, mises à jour de sécurité régulières, pare-feu
  local.
- Contrôle des autorités de certification autorisées.
- Interdiction de mémoriser les mots de passe dans le navigateur.
- Verrouillage automatique des sessions.

## Compromission d'identifiants OAuth / PISTE (§V.3)

En cas de compromission suspectée ou avérée (surconsommation anormale,
fuite du `client_secret` dans un repo public, etc.), l'Utilisateur
doit :

1. **Réinitialiser** ses identifiants sur PISTE immédiatement.
2. **Notifier** la DILA et / ou l'AIFE dans les plus brefs délais.

Pylegifrance n'effectue aucune persistance disque des jetons
(voir @docs/src/content/docs/entities/authentication.md), ce qui
réduit la surface d'exposition. Les identifiants restent dans `.env` ;
ne jamais les commiter.

## Autres contraintes (v2022)

- **Âge minimum : 15 ans** (§I.2, « majeur numérique en France »). En
  2020, majeurs uniquement ou mineurs avec autorisation parentale.
- **Notification des changements de CGU par email** (§I.3). Garder la
  boîte du compte PISTE active.
- **Contact RGPD DILA** : `rgpd@dila.gouv.fr` — remplace l'ancien
  `dpd@pm.gouv.fr` de 2020.

## Voir aussi

- [`/concepts/piste-oauth`](/pylegifrance/concepts/piste-oauth/) — flux
  d'authentification.
- [`/entities/authentication`](/pylegifrance/entities/authentication/) —
  gestion mémoire des jetons.
- [`/operations/configure-api-credentials`](/pylegifrance/operations/configure-api-credentials/) —
  placer les identifiants en dehors du repo.
