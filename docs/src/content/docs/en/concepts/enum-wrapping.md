---
title: Enum wrapping
description: Domain enums (NomCode, TypeChampCode) wrap the generated DTO enums to isolate the public API.
sidebar:
  order: 4
---

The enums used by the facades (`NomCode`, `TypeChampCode`, `SortCode`, etc.
in `pylegifrance/models/<fond>/enum.py`) **wrap** the generated enums in
`pylegifrance/models/generated/model.py`.

## Pattern

```python
# models/code/enum.py  (domain, public)
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

Domain models expose `to_generated()` for API serialization, and — where
relevant — a `from_generated()` classmethod for deserialization.

## Why

- Generated enums change on every regeneration from `legifrance.json`.
- Domain enums **stay stable** even if upstream renames or adds values.
- They also allow nice public naming (`NomCode.CC`) mapped to a raw API
  identifier (`"LEGITEXT000006070721"` or the generated enum value).

## Naming rules

- Classes: `PascalCase` (`NomCode`, `TypeChampCode`).
- Values: `UPPERCASE_WITH_UNDERSCORES` for action enums (`TypeRecherche.EXACTE`,
  `Operateur.ET`). Human-readable values (code labels) for "catalog" enums
  (`NomCode.CC`).

## See also

- [`/en/concepts/generated-models`](/pylegifrance/en/concepts/generated-models/)
- [`/en/concepts/fond-facade`](/pylegifrance/en/concepts/fond-facade/)
