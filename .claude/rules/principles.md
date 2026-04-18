# Core Principles

Apply these principles to every change. Review against them before
considering work complete.

| Principle | Check |
|---|---|
| **KISS** | Is there unnecessary complexity? Could this be simpler while achieving the same goal? |
| **DRY** | Is there duplicated logic or content? Can anything be consolidated or reused? |
| **Security by Design** | Does the change expose sensitive data, accept unvalidated input, or weaken boundaries? |
| **Performance** | Does the change introduce unnecessary allocations, N+1 queries, or render-blocking work? |
| **YAGNI** | Is anything here speculative? Remove what isn't needed now. |

## Post-implementation review (mandatory)

After **every** implementation session — before reporting the task as
complete — review the touched code (and its immediate neighbours) for
DRY and KISS opportunities:

1. Re-read the diff end-to-end. Flag any duplication introduced
   within the diff itself or between the diff and existing code.
2. Flag any complexity that does not pay for itself: premature
   abstractions, unused parameters, dead branches, speculative
   configuration knobs (YAGNI).
3. Consolidate duplicates into a single source of truth **only when
   the abstraction is obvious and load-bearing**. Three similar lines
   is not yet a pattern — prefer repetition over a bad abstraction.