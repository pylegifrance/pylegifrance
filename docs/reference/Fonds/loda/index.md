# LODA

La classe `Loda` fournit une interface pour accéder au fond LODA (Lois, Ordonnances, Décrets, Arrêtés) de l'API Legifrance.

## Initialisation

```python
from pylegifrance.client import LegifranceClient
from pylegifrance.fonds.loda import Loda

client = LegifranceClient()
loda = Loda(client)
```

## Méthodes principales

### fetch

```python
def fetch(self, text_id: str) -> Optional[TexteLoda]:
```

Récupère un texte par son identifiant.

### fetch_version_at

```python
def fetch_version_at(self, text_id: str, date: str) -> Optional[TexteLoda]:
```

Récupère une version d'un texte à une date spécifique.

### fetch_versions

```python
def fetch_versions(self, text_id: str) -> List[TexteLoda]:
```

Récupère toutes les versions d'un texte.

### search

```python
def search(self, query: SearchRequest | str) -> List[TexteLoda]:
```

Recherche des textes correspondant à la requête. La requête peut être une chaîne de caractères simple ou un objet SearchRequest pour des recherches plus avancées.

## Classe SearchRequest

```python
class SearchRequest:
    text_id: str = ""
    search: str = None
    champ: str = "NUM_ARTICLE"
    type_recherche: str = "EXACTE"
    fond: str = "LODA_DATE"
    nature: List[str] = ["LOI", "ORDONNANCE", "DECRET", "ARRETE"]
    date_signature: List[str] = None
    page_number: int = 1
    page_size: int = 10
```

Permet de construire des requêtes de recherche avancées pour le fond LODA.
