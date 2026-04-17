---
title: Fetch a case law decision
description: Access the content of decisions via JuriAPI.
sidebar:
  order: 6
---

The [`JuriAPI`](/pylegifrance/en/entities/fond-juri/) class lets you fetch
decisions by identifier or by keywords.

## Instantiate JuriAPI

```python
from pylegifrance.fonds.juri import JuriAPI

juri = JuriAPI(client)
```

## Fetch a decision

```python
# By identifier
decision = juri.fetch("JURITEXT000037999394")

# By legacy identifier
decision = juri.fetch_with_ancien_id("07-87362")
```

## Access the content

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

## Search without an identifier

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

if results:
    first = results[0]
    content = first.text
```

## Versions of a decision

```python
dated = decision.at("2022-01-01")
latest = decision.latest()
all_versions = decision.versions()
```

Each returns a `JuriDecision` (or a list).

## See also

- [`/en/entities/fond-juri`](/pylegifrance/en/entities/fond-juri/)
- [`/en/references/juri`](/pylegifrance/en/references/juri/)
