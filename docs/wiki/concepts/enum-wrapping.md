---
title: Enum wrapping
description: Les enums de domaine (NomCode, TypeChampCode) encapsulent les enums DTO générés pour isoler l'API publique.
sidebar:
  order: 4
---

Les enums utilisé·e·s par les façades (`NomCode`, `TypeChampCode`, `SortCode`,
etc. dans `pylegifrance/models/<fond>/enum.py`) **encapsulent** les enums
générés dans `pylegifrance/models/generated/model.py`.

## Pattern

```python
# models/code/enum.py  (domaine, public)
class NomCode(str, Enum):
    CC = "Code civil"
    CP = "Code pénal"
    # …

    def to_generated(self) -> GeneratedNomCode:
        return GeneratedNomCode(self.value)

    @classmethod
    def from_generated(cls, g: GeneratedNomCode) -> "NomCode":
        return cls(g.value)
```

Les modèles de domaine exposent `to_generated()` pour la sérialisation API,
et — quand c'est pertinent — un `from_generated()` classmethod pour la
désérialisation.

## Pourquoi

- Les enums générés changent à chaque régénération depuis `legifrance.json`.
- Les enums de domaine **restent stables** même si l'upstream renomme ou
  ajoute des valeurs.
- Ça permet de nommer joliment côté public (`NomCode.CC`) et de mapper vers
  un identifiant brut côté API (`"LEGITEXT000006070721"` ou la valeur
  enum générée).

## Règles de nommage

- Classes : `PascalCase` (`NomCode`, `TypeChampCode`).
- Valeurs : `MAJUSCULES_AVEC_TIRETS_BAS` pour les enums d'action
  (`TypeRecherche.EXACTE`, `Operateur.ET`). Valeurs lisibles (libellés de
  code) pour les enums « catalogue » (`NomCode.CC`).

## Voir aussi

- [`/concepts/generated-models`](/pylegifrance/concepts/generated-models/)
- [`/concepts/fond-facade`](/pylegifrance/concepts/fond-facade/)
