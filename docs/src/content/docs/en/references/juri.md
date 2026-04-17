---
title: JuriAPI
description: Reference for the JuriAPI facade (case law).
sidebar:
  order: 4
---

```python
class JuriAPI:
    def __init__(self, client: LegifranceClient)

    def fetch(self, text_id: str) -> JuriDecision | None
    def fetch_with_ancien_id(self, ancien_id: str) -> JuriDecision | None
    def fetch_by_id(self, text_id: str) -> JuriDecision | None
    def fetch_version_at(self, text_id: str, date: str) -> JuriDecision | None
    def fetch_versions(self, text_id: str) -> list[JuriDecision]

    def search(self, query: str | SearchRequest) -> list[JuriDecision]
    def search_by_ecli(
        self, ecli: str, *, fond: str = "JURI"
    ) -> list[JuriDecision]
    def search_by_affaire(
        self,
        num_affaire: str,
        *,
        formation: str | None = None,
        date_decision: date | None = None,
        date_range: tuple[date, date] | None = None,
    ) -> list[JuriDecision]
```

Provides methods to fetch and search case law decisions.

## JuriDecision (main properties)

`text`, `text_html`, `title`, `long_title`, `formation`, `numero`,
`jurisdiction`, `solution`, `date`, `id`, `url`, `cid`, `eli`, `nor`, `ecli`,
`citations`.

Version methods: `at(date)`, `latest()`, `versions()`.

## See also

- [`/en/entities/fond-juri`](/pylegifrance/en/entities/fond-juri/)
- [`/en/operations/fetch-case-law`](/pylegifrance/en/operations/fetch-case-law/)
