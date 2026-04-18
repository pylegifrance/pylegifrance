---
title: Fond Code
description: Façade pour rechercher et consulter les codes juridiques français (Code civil, Code pénal, etc.).
sidebar:
  order: 4
---

La classe `Code` (dans `pylegifrance/fonds/code.py`) est la façade qui expose
l'API fluide pour chercher dans les codes français.

## Portée

Le fond regroupe les codes (Code civil, Code pénal, Code de commerce…) servis
via deux bases Legifrance :

- `CODE_ETAT` — état actuel des codes (par défaut) ;
- `CODE_DATE` — état historique à une date donnée.

Par défaut, les recherches portent sur les articles en vigueur à la date du
jour. Pour une recherche historique, utiliser
[`.at_date("YYYY-MM-DD")`](/pylegifrance/concepts/builder-pattern/) ou initialiser avec
`Code(client, fond="CODE_DATE")`.

## Usage

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.code import Code
from pylegifrance.models.code.enum import NomCode

client = LegifranceClient(client_id="...", client_secret="...")
code = Code(client)

# Article 1382 du Code civil
resultats = (
    code.search()
        .in_code(NomCode.CC)
        .article_number("1382")
        .execute()
)
```

## Composants exposés

- `code.search()` → `CodeSearchBuilder` (fluent, voir
  [`/concepts/builder-pattern`](/pylegifrance/concepts/builder-pattern/)).
- `code.fetch_code(text_id)` → consult d'un LEGITEXT entier.
- `code.fetch_article(article_id)` → article par LEGIARTI.

## Codes fréquents

| Enum | Code | LEGITEXT |
|---|---|---|
| `NomCode.CC` | Code civil | `LEGITEXT000006070721` |
| `NomCode.CP` | Code pénal | `LEGITEXT000006070719` |
| `NomCode.CCOM` | Code de commerce | `LEGITEXT000005634379` |
| `NomCode.CTRAV` | Code du travail | `LEGITEXT000006072050` |
| `NomCode.CPC` | Code de procédure civile | `LEGITEXT000006070716` |
| `NomCode.CPP` | Code de procédure pénale | `LEGITEXT000006071154` |

Liste complète : [legifrance.gouv.fr/liste/code?etatTexte=VIGUEUR](https://www.legifrance.gouv.fr/liste/code?etatTexte=VIGUEUR).

## Voir aussi

- [How-to : rechercher dans les codes](/pylegifrance/operations/search-legal-code/)
- [Référence API](/pylegifrance/references/code/)
- [`/concepts/enum-wrapping`](/pylegifrance/concepts/enum-wrapping/) — pourquoi `NomCode`
  n'est pas directement l'enum généré.

:::caution
Il est de la responsabilité exclusive de l'utilisateur·rice de vérifier que
les informations renvoyées par l'API sont pertinentes et à jour.
:::
