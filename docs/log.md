# Log

## [2026-04-17] migration | Passage de MkDocs Material à Astro Starlight + structure wiki plate

- Ancienne structure Diátaxis (`tutoriels/`, `guides-pratiques/`, `reference/`,
  `explication/`) remplacée par `entities/`, `concepts/`, `operations/`,
  `references/` sous `src/content/docs/`.
- Site généré par Astro Starlight (locale racine = français, `/en/` pour
  l'anglais avec fallback automatique).
- Plugin `starlight-llms-txt` activé — expose `/llms.txt` et `/llms-full.txt`
  pour consommation par agents IA.
- Raw sources initiales sous `raw/legifrance/` : `lexique-api-lgf.docx`,
  `exemples-d-utilisation-de-l-api.docx`,
  `description-des-tris-et-filtres-de-l-api.xlsx` (docs officielles PISTE,
  téléchargées le 2026-04-14).
- `docs/CLAUDE.md` (nested) ajouté comme schéma de maintenance ; le
  `CLAUDE.md` racine reste inchangé.
- `.github/CONTRIBUTING.md` et `.github/ISSUE_TEMPLATE/story.yml` mis à jour
  pour collecter les prompts LLM des demandes de fonctionnalité (voir
  `raw/prompts/`).
- `pyproject.toml` : groupe `[project.optional-dependencies].docs` (mkdocs +
  plugins) supprimé. `mkdocs.yml` supprimé.
- Déploiement GitHub Pages via `.github/workflows/docs.yml`
  (`withastro/action` + `actions/deploy-pages`).

## [2026-04-17] translation | Miroir anglais complet

- Toutes les pages `src/content/docs/*` dupliquées sous `en/` en traduction
  intégrale (7 entities, 6 concepts, 7 operations, 5 references + catalogue).
- Liens internes des pages EN pointent vers `/pylegifrance/en/…`.
- Le commentaire initial du `en/index.mdx` (« most pages in French only,
  fallback applies ») supprimé : ce n'est plus vrai, la traduction est à
  parité.
- Build : 53 pages.

## [2026-04-17] fix | Corrections de signatures et localisation du sidebar

- `references/juri.md` (FR+EN) : `search_by_ecli` corrigé en
  `list[JuriDecision]` (était `JuriDecision | None`), ajout de
  `fetch_by_id`, `| None` ajouté aux méthodes `fetch*`.
- `references/client.md` (FR+EN) : `data: Any` au lieu de `data: str`,
  ajout de `create` (classmethod) et `close`.
- `references/code.md` + `operations/search-legal-code.md` (FR+EN) : retour
  d'`execute()` corrigé en `list[Article]` (était `dict`).
- `entities/article.md` (FR+EN) : remplacement du dict-de-résultat ancien
  par le vrai modèle Pydantic (champs `id`, `number`, `content`,
  `content_html`, `legal_status`, `version_date`, …).
- `astro.config.mjs` : labels de groupe sidebar localisés via
  `translations` (Entités/Concepts/Opérations/Référence en FR,
  Entities/Concepts/Operations/Reference en EN).
- `index.mdx` (FR) : titres de sections traduits en français
  (`Entités`, `Opérations`, `Référence`).
- Workflows GitHub Actions bumpés aux dernières versions :
  `actions/checkout@v6`, `actions/deploy-pages@v5`, `withastro/action@v6`.

## [2026-04-17] ingest | Sources officielles Legifrance (lexique + exemples + tris/filtres)

- Extraction texte des 3 fichiers binaires de `raw/legifrance/` sauvegardée
  en `.txt` companion (via `zipfile` + ElementTree, sans dépendances
  supplémentaires) :
  - `lexique-api-lgf.txt` — 16 449 car.
  - `exemples-d-utilisation-de-l-api.txt` — 23 147 car.
  - `description-des-tris-et-filtres-de-l-api.txt` — 32 711 car.
- Nouvelle page concept `cid-and-versioning.md` (FR+EN) : documente le CID
  (Common Identifier), le principe de consolidation, les états juridiques
  complets (`VIGUEUR`, `VIGUEUR_AVEC_TERME`, `VIGUEUR_DIFFEREE`, `ABROGE`,
  `ABROGE_DIFF`, `MODIFIE`) et les dispositions « balai ». Sourcé du
  lexique.
- `entities/article.md` (FR+EN) : champ `legal_status` pointe désormais
  vers la page complète des états juridiques.
- `concepts/piste-oauth.md` (FR+EN) : ajout de `scope=openid`, URL de
  l'endpoint sandbox PISTE, durée `expires_in=3600 s`. Sourcé des exemples
  officiels §1.
- `index.mdx` (FR+EN) : entrée `CID & versioning` ajoutée au catalogue.
- À suivre : intégrer les tris/filtres par fond (JUFI, KALI, ACCO, CNIL,
  etc.) dans les pages `references/` respectives — nécessite de nouvelles
  façades côté code (pour KALI/BOCC/ACCO/CNIL/débats/questions/docAdmin
  notamment ; pas encore exposés par pylegifrance).

## [2026-04-18] ingest | CGU PISTE de l'API Légifrance Beta

- Téléchargé `cgu-piste-legifrance-beta.pdf` (674 KB, v2, DILA) depuis
  [piste.gouv.fr/images/cgu/DILA_Legifrance_Beta_v2.pdf](https://piste.gouv.fr/images/cgu/DILA_Legifrance_Beta_v2.pdf).
  Text extract via `pdftotext -layout` : `cgu-piste-legifrance-beta.txt`
  (400 lignes).
- Nouvelle page concept `concepts/api-terms-and-quotas.md` (FR+EN)
  documentant : statut bêta sans SLA (§IV.1), quotas PISTE
  req/s/min/jour consultables dans la console PISTE (§IV.3), licence
  Etalab 2.0 sur les données exposées (§IX), procédure de
  compromission d'identifiants OAuth (§V.3).
- `concepts/piste-oauth` (FR+EN) enrichi : le paragraphe « 429 » pointe
  désormais vers la nouvelle page pour les quotas exacts.
- `index.mdx` (FR+EN) : entrée « CGU, quotas et licence » ajoutée au
  catalogue.
- Tentative de mirroring des deux CGU `legifrance.gouv.fr` bloquée par
  Cloudflare (challenge JS) ; URLs référencées dans `raw/README.md`
  pour téléchargement manuel.
- Le schéma OpenAPI officiel existe déjà en repo
  (`@pylegifrance/models/generated/legifrance.json`) ; référencé depuis
  `raw/README.md` plutôt que dupliqué.

## [2026-04-18] ingest | CGU API Légifrance v1.0 (15/12/2022) — téléchargement manuel

- Ajouté `cgu-legifrance-api.pdf` (273 KB, v1.0 DILA du 15/12/2022 —
  **version canonique actuelle**) et `conditions-generales-d-utilisation-de-l-api.docx`
  (53 KB, source éditable) après téléchargement manuel par le mainteneur
  (Cloudflare bloquait l'accès programmatique). Text extracts :
  `cgu-legifrance-api.txt` (433 lignes) et
  `conditions-generales-d-utilisation-de-l-api.txt` (344 lignes).
- Diff contre la v1.1 de 2020 (PISTE) a révélé plusieurs changements
  substantiels intégrés dans `concepts/api-terms-and-quotas.md` (FR+EN) :
  - **§IV.1** : introduction d'un engagement de moyens **95 % par
    jour** sur prod (la v2020 n'avait aucun engagement). Pas
    d'engagement sur sandbox.
  - **§I.1** : la licence Etalab 2.0 est désormais explicitement dans
    le périmètre des CGU (était implicite en 2020).
  - **§I.2** : âge minimum clarifié → 15 ans (majeur numérique en
    France). En 2020 : majeur ou mineur avec autorisation parentale.
  - **§V.1** : baseline sécurité ajoute référence explicite aux
    recommandations **CNIL et ANSSI**.
  - **§I.3 / §IV.3** : notifications de changement de CGU / quotas
    désormais « par email » (explicite), plus « tout autre moyen ».
  - **§X** : contact RGPD DILA = `rgpd@dila.gouv.fr` (remplace
    `dpd@pm.gouv.fr` de 2020), nouvelle adresse postale
    26 rue Desaix, 75727 Paris Cedex 15.
- La page concept a été restructurée autour des CGU 2022 comme source
  principale, avec la v2020 conservée comme source historique.
- `raw/README.md` mis à jour : les trois CGU sont désormais toutes
  mirrorées localement, la note « non mirrorées » est supprimée, et
  les versions/dates sont indiquées.

## [2026-04-18] refactor | Flux de contribution PR-first (issues désactivées)

- Issues GitHub désactivées côté repo → flux de contribution collapsé
  en « créer une branche + ouvrir une PR » directement, sans étape
  intermédiaire.
- `.github/CONTRIBUTING.md` réécrit : ajoute une note explicite
  « issues désactivées », détaille le nommage de branche
  Conventional-Commits-friendly, référence le nouveau modèle de PR,
  explique que `pre-commit install` couvre maintenant les deux stages.
- `.github/PULL_REQUEST_TEMPLATE.md` créé avec les sections de
  l'ancien story.yml (problématique, tests BDD, critères d'acceptation)
  plus une section « Prompt LLM utilisé (optionnel) » à la place du
  champ d'issue form.
- `.github/ISSUE_TEMPLATE/story.yml` supprimé (dead weight puisque les
  issues sont désactivées). Répertoire `ISSUE_TEMPLATE/` supprimé avec.
- `docs/raw/prompts/README.md` : convention de nommage et format
  frontmatter basculés d'`issue` vers `pr` (`YYYY-MM-DD-pr-<n>-<slug>.md`,
  frontmatter `pr:` / `url: pulls/<n>`).
- L'entrée du log de [2026-04-17] « LLM transparency workflow »
  n'est pas réécrite (log append-only, cf. @docs/CLAUDE.md § 10).
