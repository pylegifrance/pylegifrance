# Wiki pylegifrance — schéma de maintenance

> Règles projet : voir @CLAUDE.md. Ce fichier ajoute les conventions du
> wiki ; Claude Code le charge automatiquement quand le répertoire de travail
> est sous `docs/`.

## 1. Qu'est-ce que ce wiki

Une base de connaissances **maintenue par des LLM** pour la librairie
`pylegifrance`. Trois couches :

- **Sources immuables** — `raw/` (docx, xlsx, prompts d'issues, extraits de
  l'API officielle). On lit, on n'écrit pas.
- **Pages dérivées** — `src/content/docs/` (entities, concepts, operations,
  references). Générées et tenues à jour par le LLM à partir des sources et
  des discussions avec les mainteneur·se·s.
- **Schéma** — ce fichier + @CLAUDE.md. Dit au LLM comment ingérer,
  requêter, et maintenir le wiki.

## 2. Structure des répertoires

```
docs/
  CLAUDE.md              ← ce fichier
  log.md                 ← journal append-only
  astro.config.mjs       ← config Starlight + i18n
  package.json           ← deps Astro
  raw/                   ← sources immuables
    legifrance/          ← docs officielles PISTE
    prompts/             ← prompts LLM des issues
  public/                ← fichiers statiques (robots.txt, favicon)
  src/
    assets/logo.svg
    content.config.ts    ← collections Starlight (docs + i18n)
    styles/custom.css
    content/docs/        ← pages rendues (chemin imposé par Starlight)
      index.mdx          ← catalogue
      entities/          ← une page par chose de 1ʳᵉ classe
      concepts/          ← patterns, décisions d'archi
      operations/        ← how-to lecteurs
      references/        ← référence API
      en/                ← miroir anglais (partiel, fallback auto)
```

## 3. Types de pages

| Type | Rôle | Exemples |
|---|---|---|
| `entities/` | Une page par objet de 1ʳᵉ classe (classe, fond, modèle). Source de vérité pour le LLM. | `legifrance-client`, `fond-code`, `fond-juri`, `article` |
| `concepts/` | Patterns, décisions architecturales, explications « pourquoi ». | `builder-pattern`, `enum-wrapping`, `piste-oauth` |
| `operations/` | How-to orientés utilisateur final (tutoriels + guides). | `getting-started`, `search-legal-code` |
| `references/` | Référence API (signatures, paramètres). Dérivée des entities. | `client`, `code`, `juri`, `loda` |

## 4. Front matter des pages

Minimum Starlight :

```yaml
---
title: Nom de la page
description: Une phrase pour SEO et pour l'index.
---
```

Optionnel, utilisé par le LLM pour la maintenance :

```yaml
---
title: …
description: …
sidebar: { order: 2 }       # override l'ordre alpha si besoin
sources:                    # @paths depuis la racine du repo
  - "@docs/raw/legifrance/lexique-api-lgf.md"
related:                    # slugs d'autres pages
  - /concepts/builder-pattern
  - /references/code
updated: 2026-04-17
---
```

## 5. Règles linguistiques

- **Contenu** : français par défaut (locale racine). Miroir anglais sous
  `en/…` quand disponible ; sinon Starlight affiche automatiquement la version
  française avec une bannière « not yet translated ».
- **Identifiants de code** (noms de classes, fonctions, variables, types) : en
  anglais, conformément à @.claude/rules/coding.md.
- **Exemples de code** : commentaires en français autorisés, identifiants en
  anglais.

## 6. Liens internes

Utiliser des URL Starlight absolues avec le slug basé sur le nom de fichier :

```markdown
Voir [le pattern builder](/concepts/builder-pattern/) pour les détails.
```

Starlight résout automatiquement `.md`/`.mdx` vers `/slug/`. Pas de lien
relatif inter-dossier (fragile au refactor).

## 7. Opération : Ingest

Quand une nouvelle source arrive dans `raw/` :

1. Lire la source (si binaire, l'extraire en texte d'abord).
2. Discuter les points clés avec le mainteneur·se.
3. Identifier les pages touchées :
   - un nouvel objet → créer une page `entities/<slug>.md`
   - une règle/architecture → `concepts/<slug>.md`
   - un cas d'usage → `operations/<slug>.md`
   - une API → `references/<slug>.md`
4. Mettre à jour les `related:` des pages voisines.
5. Mettre à jour `src/content/docs/index.mdx` (catalogue).
6. Ajouter une entrée à `log.md` :
   `## [YYYY-MM-DD] ingest | <titre de la source>`.

## 8. Opération : Query

Pour répondre à une question :

1. Lire `src/content/docs/index.mdx` pour repérer les pages pertinentes.
2. Descendre dans les pages nécessaires ; citer avec liens Starlight absolus.
3. Si la synthèse est non-triviale et réutilisable, la filer comme nouvelle
   page (`operations/` pour un how-to, `concepts/` pour une explication) —
   ajouter une entrée `query` au `log.md`.

## 9. Opération : Lint

Checklist périodique :

- Pages orphelines (aucun lien entrant depuis `index.mdx` ou `related:`).
- `updated:` vieux de plus de 6 mois → vérifier que le contenu est toujours
  juste par rapport au code.
- Liens internes cassés (`pnpm build` avec mode strict les attrape).
- Contradictions entre pages (surtout `references/` vs `entities/`).
- Concepts mentionnés mais sans page dédiée.
- Entities manquantes dans `references/`.

Logguer la passe avec
`## [YYYY-MM-DD] lint | <brève description>`.

## 10. Format du log

`log.md` est append-only et grep-friendly :

```markdown
## [2026-04-17] ingest | Lexique API Legifrance
- Ajouté entity `article.md` pour clarifier le modèle Article.
- Mis à jour `entities/fond-code.md` avec la terminologie LEGIARTI.
```

`grep "^## \[" log.md | tail -5` donne les 5 dernières activités.

## 11. Dev local

```bash
cd docs
pnpm install
pnpm dev      # serveur de dev : http://localhost:4321/pylegifrance
pnpm build    # sortie statique dans dist/
```

Le plugin `starlight-llms-txt` génère `dist/llms.txt` et `dist/llms-full.txt`
à chaque build — à utiliser pour donner le wiki en contexte à un LLM externe.
