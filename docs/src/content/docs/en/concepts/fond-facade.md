---
title: Fond facade
description: Facade pattern per documentary fond (Code, Juri, LODA) to isolate the public API from generated DTOs.
sidebar:
  order: 3
---

Each Legifrance **fond** (Code, Juri, LODA, JORF…) has its own facade in
`pylegifrance/fonds/`. A facade:

1. takes a [`LegifranceClient`](/pylegifrance/en/entities/legifrance-client/)
   (and an optional `fond` parameter to pick the base — e.g. `CODE_DATE` vs
   `CODE_ETAT`);
2. exposes `.search()` which returns a **fluent builder**
   ([see `/en/concepts/builder-pattern`](/pylegifrance/en/concepts/builder-pattern/));
3. exposes `.fetch_*()` methods returning **fetchers** (a more focused builder
   pattern).

## Design invariant

> Anything outside `pylegifrance/fonds/*` and `pylegifrance/__init__.py` is
> considered **internal**.

Users never instantiate the `models/generated/` models directly — they always
go through the facade, which composes domain models (`models/<fond>/`) and
converts them to generated DTOs (`to_generated()`) before the API call.

## Benefits

- **Public stability**: the Legifrance OpenAPI schema can change without
  breaking the pylegifrance API.
- **Ergonomics**: the facade offers shortcuts (e.g. `search("word")` for
  simple cases).
- **Enrichment**: objects returned by the facade have business methods (e.g.
  `decision.at(date)`) absent from the raw DTO.

## See also

- [`/en/concepts/architecture`](/pylegifrance/en/concepts/architecture/)
- [`/en/concepts/enum-wrapping`](/pylegifrance/en/concepts/enum-wrapping/)
