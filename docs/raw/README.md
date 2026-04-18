# raw/ — Sources immuables du wiki

Ce dossier contient les **sources brutes** que les LLM lisent pour maintenir le
wiki (@docs/src/content/docs/). Les fichiers ici ne sont **jamais modifiés**
par le wiki : on ajoute, on ne réécrit pas. Voir @docs/CLAUDE.md pour le
workflow d'ingestion.

Convention : les fichiers binaires (PDF, DOCX, XLSX) restent dans leur format
d'origine ; les LLM les convertissent en texte lors de la lecture.

## Sous-dossiers

- `legifrance/` — documentation officielle Legifrance, téléchargée depuis
  la [page Open data et API de legifrance.gouv.fr](https://www.legifrance.gouv.fr/contenu/pied-de-page/open-data-et-api) :
  - [Lexique](https://www.legifrance.gouv.fr/contenu/Media/files/lexique-api-lgf.docx) → `lexique-api-lgf.docx`
  - [Exemples d'utilisation](https://www.legifrance.gouv.fr/contenu/Media/Files/pied-de-page/exemples-d-utilisation-de-l-api.docx) → `exemples-d-utilisation-de-l-api.docx`
  - [Description des tris et filtres](https://www.legifrance.gouv.fr/contenu/Media/Files/pied-de-page/description-des-tris-et-filtres-de-l-api.xlsx) → `description-des-tris-et-filtres-de-l-api.xlsx`
  - [CGU PISTE de l'API Légifrance Beta (v2)](https://piste.gouv.fr/images/cgu/DILA_Legifrance_Beta_v2.pdf) → `cgu-piste-legifrance-beta.pdf`

  Chaque binaire est accompagné d'un `.txt` companion (extrait texte brut
  obtenu via `zipfile`+ElementTree pour docx/xlsx et `pdftotext -layout`
  pour les PDF) afin de faciliter l'ingestion par LLM.

  **Sources officielles non mirrorées** (téléchargement programmatique
  bloqué par Cloudflare — à récupérer manuellement si besoin) :

  - [CGU Légifrance API v1.1](https://www.legifrance.gouv.fr/contenu/Media/files/pied-de-page/cgu-legifrance-api-vf-15-12-2022_0.pdf)
  - [Conditions générales d'utilisation de l'API Légifrance (docx)](https://www.legifrance.gouv.fr/contenu/Media/Files/pied-de-page/conditions-generales-d-utilisation-de-l-api-legifrance.docx)

  Le schéma OpenAPI de l'API (source de `@pylegifrance/models/generated/model.py`)
  vit dans le repo à `@pylegifrance/models/generated/legifrance.json` —
  il n'est pas dupliqué ici.
- `prompts/` — prompts LLM déposés par les contributeurs via les issues
  (voir `prompts/README.md`).

## Exclusion du build

Ce dossier n'est **pas** dans `src/content/docs/`, donc Astro ne le rend pas
publiquement. Il reste versionné dans le repo pour la maintenance du wiki.
