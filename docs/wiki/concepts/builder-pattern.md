---
title: Builder pattern
description: API fluide pour composer des requêtes de recherche lisibles et typées.
sidebar:
  order: 2
---

Chaque façade expose un **builder** fluide qui compose une requête par
enchaînement de méthodes, terminé par `.execute()`.

## Exemple : `Code.search()`

```python
resultats = (
    code.search()
        .in_code(NomCode.CC)
        .article_number("1382")
        .with_formatter()
        .execute()
)
```

Les builders retournent `Self` pour permettre le chaînage ; ils prennent le
[`LegifranceClient`](/pylegifrance/entities/legifrance-client/) en premier argument.

## Builders existants

| Builder | Point d'entrée | Méthodes typiques |
|---|---|---|
| `CodeSearchBuilder` | `Code.search()` | `.in_code()`, `.text()`, `.article_number()`, `.at_date()`, `.with_formatter()`, `.paginate()`, `.execute()` |
| `CodeConsultFetcher` | `Code.fetch_code(id)` | `.include_abrogated()`, `.section()`, `.at(date)` |
| `ArticleFetcher` | `Code.fetch_article(id)` | `.at(date)` |

## Pourquoi un builder plutôt qu'un gros `dataclass` ?

- **Lisibilité** : la requête se lit comme une phrase.
- **Progressivité** : chaque étape est optionnelle et composable.
- **Typage** : chaque méthode restreint les paramètres licites (ex. `in_code`
  accepte un `NomCode`, pas un `str`).
- **Découverte** : l'auto-complétion guide l'utilisateur·rice vers les
  méthodes valides.

## Voir aussi

- [`/entities/fond-code`](/pylegifrance/entities/fond-code/)
- [Référence API `/references/code`](/pylegifrance/references/code/)
