---
title: Fond Juri
description: Facade to fetch and search case law decisions.
sidebar:
  order: 5
---

The `JuriAPI` class (in `pylegifrance/fonds/juri.py`) exposes access to the
`JURI` (case law) fond of Legifrance.

## Fetching a decision

By identifier or by legacy identifier:

```python
from pylegifrance.fonds.juri import JuriAPI

juri = JuriAPI(client)

decision = juri.fetch("JURITEXT000037999394")
decision = juri.fetch_with_ancien_id("07-87362")
```

The return is an enriched `JuriDecision`.

## Accessing content

```python
decision.text          # full text
decision.text_html     # formatted HTML
decision.title
decision.long_title
decision.formation
decision.numero
decision.jurisdiction
decision.solution
decision.date
```

## Search

```python
from pylegifrance.fonds.juri import SearchRequest
from pylegifrance.models.juri.constants import JuridictionJudiciaire

# Simple
results = juri.search("responsabilité civile")

# Advanced
request = SearchRequest(
    search="contrat",
    juridiction_judiciaire=[JuridictionJudiciaire.cour_de_cassation.value],
    page_size=5,
)
results = juri.search(request)
```

## Versions of a decision

```python
decision.at("2022-01-01")   # version at a date
decision.latest()            # latest version
decision.versions()          # all versions
```

## See also

- [How-to: fetch a decision](/pylegifrance/en/operations/fetch-case-law/)
- [API reference](/pylegifrance/en/references/juri/)
