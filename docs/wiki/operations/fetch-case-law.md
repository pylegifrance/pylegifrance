---
title: Récupérer une décision de jurisprudence
description: Accéder au contenu des décisions via JuriAPI.
sidebar:
  order: 6
---

La classe [`JuriAPI`](/pylegifrance/entities/fond-juri/) permet de récupérer des décisions
par identifiant ou par mots-clés.

## Instancier JuriAPI

```python
from pylegifrance.fonds.juri import JuriAPI

juri = JuriAPI(client)
```

## Récupérer une décision

```python
# Par identifiant
decision = juri.fetch("JURITEXT000037999394")

# Par ancien identifiant
decision = juri.fetch_with_ancien_id("07-87362")
```

## Accéder au contenu

```python
decision.text          # texte intégral
decision.text_html     # HTML formaté
decision.title
decision.long_title
decision.formation
decision.numero
decision.jurisdiction
decision.solution
decision.date
```

## Rechercher sans identifiant

```python
from pylegifrance.fonds.juri import SearchRequest
from pylegifrance.models.juri.constants import JuridictionJudiciaire

# Simple
resultats = juri.search("responsabilité civile")

# Avancée
requete = SearchRequest(
    search="contrat",
    juridiction_judiciaire=[JuridictionJudiciaire.cour_de_cassation.value],
    page_size=5,
)
resultats = juri.search(requete)

if resultats:
    premiere = resultats[0]
    contenu = premiere.text
```

## Versions d'une décision

```python
version_a_date = decision.at("2022-01-01")
derniere = decision.latest()
toutes = decision.versions()
```

Chacune renvoie un `JuriDecision` (ou une liste).

## Voir aussi

- [`/entities/fond-juri`](/pylegifrance/entities/fond-juri/)
- [`/references/juri`](/pylegifrance/references/juri/)
