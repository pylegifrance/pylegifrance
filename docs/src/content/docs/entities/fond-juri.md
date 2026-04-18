---
title: Fond Juri
description: Façade pour récupérer et rechercher les décisions de jurisprudence.
sidebar:
  order: 5
---

La classe `JuriAPI` (dans `pylegifrance/fonds/juri.py`) expose l'accès au fond
`JURI` (jurisprudence) de Legifrance.

## Récupération d'une décision

Par identifiant ou par ancien identifiant :

```python
from pylegifrance.fonds.juri import JuriAPI

juri = JuriAPI(client)

decision = juri.fetch("JURITEXT000037999394")
decision = juri.fetch_with_ancien_id("07-87362")

# Vérification par identifiant canonique (v1.3.2)
decision = juri.fetch_by_id("JURITEXT000037999394")
```

## Recherche par ECLI ou par affaire

```python
# Par identifiant ECLI européen (v1.3.2)
resultats = juri.search_by_ecli("ECLI:FR:CCASS:2019:C200148")

# Par numéro d'affaire — style Cour de cassation (v1.3.2)
from datetime import date
resultats = juri.search_by_affaire(
    "07-87.362",
    formation="chambre criminelle",
    date_decision=date(2008, 1, 22),
)
```

Le retour est un `JuriDecision` enrichi.

## Accès au contenu

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

## Recherche

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
```

## Versions d'une décision

```python
decision.at("2022-01-01")   # version à une date
decision.latest()            # dernière version
decision.versions()          # toutes les versions
```

## Voir aussi

- [How-to : récupérer une décision](/pylegifrance/operations/fetch-case-law/)
- [Référence API](/pylegifrance/references/juri/)
