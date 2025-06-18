---
title: Tutoriels
---
# Tutoriels

## Premier pas avec PyLegifrance

### Exemple de base

```python
from pylegifrance import LegifranceClient
from pylegifrance.fonds.code import Code
from pylegifrance.models.code.enum import NomCode

# Initialisation
client = LegifranceClient(client_id="...", client_secret="...")
code = Code(client)

# Rechercher l'article 1382 du Code civil
resultat = (code.search()
              .in_code(NomCode.CC)  # Code civil
              .article_number("1382")
              .execute())
print(resultat)
```

## Exemples avancés

### Recherche par mots-clés

```python
from pylegifrance.client import LegifranceClient
from pylegifrance.fonds.loda import Loda
from pylegifrance.models.loda.search import SearchRequest

# Initialisation
client = LegifranceClient()
loda_api = Loda(client)

# Rechercher "données personnelles" dans la loi informatique et libertés
resultats = loda_api.search(SearchRequest(
    text_id="78-17",
    champ="ARTICLE",
    type_recherche="TOUS_LES_MOTS_DANS_UN_CHAMP"
))
```

### Filtrage par date et type

```python
# Rechercher les décrets sur l'environnement de 2022
resultats = loda_api.search(SearchRequest(
    search="environnement",
    champ="TITLE",
    nature=["DECRET"],
    date_signature=["2022-01-01", "2022-12-31"]
))
```

### Formatage des résultats

```python
# Avec formatage
resultat_formate = (code.search()
                      .in_code(NomCode.CC)  # Code civil
                      .article_number("16")
                      .with_formatter()
                      .execute())
```
