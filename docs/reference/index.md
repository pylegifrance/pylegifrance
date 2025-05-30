# Référence API

## Fonctions principales

### recherche_code

```python
def recherche_code(
    code_name: str,
    search: str = None,
    champ: str = "NUM_ARTICLE",
    type_recherche: str = "EXACTE",
    fond: str = "CODE_DATE",
    formatter: bool = False,
    page_number: int = 1,
    page_size: int = 10,
    *args,
)
```

Recherche dans les codes français.

### recherche_LODA

```python
def recherche_LODA(
    text_id: str = "",
    search: str = None,
    champ: str = "NUM_ARTICLE",
    type_recherche: str = "EXACTE",
    fond: str = "LODA_DATE",
    nature: List = ["LOI", "ORDONNANCE", "DECRET", "ARRETE"],
    date_signature: List = None,
    formatter: bool = False,
    page_number: int = 1,
    page_size: int = 10,
    *args,
)
```

Recherche dans les lois, ordonnances, décrets et arrêtés.

### recherche_JURI

```python
def recherche_JURI(
    search: str = None,
    champ: str = "ALL",
    type_recherche: str = "EXACTE",
    fond: str = "JURI",
    formatter: bool = False,
    page_number: int = 1,
    page_size: int = 10,
    *args,
)
```

Recherche dans la jurisprudence (en développement).

## Classes principales

### LegifranceClient

```python
class LegifranceClient:
    def __init__(config: Optional[ApiConfig] = None)
    def update_api_keys(self, legifrance_api_key=None, legifrance_api_secret=None)
    def call_api(self, route: str, data: str)
    def ping(self, route: str = "consult/ping")
    def get(self, route: str)
```

Gère l'authentification et les appels à l'API Legifrance.

### ApiConfig

```python
class ApiConfig:
    def __init__(
        client_id: str,
        client_secret: str,
        token_url: str = "...",
        api_url: str = "...",
        connect_timeout: float = 3.05,
        read_timeout: float = 27.0,
    )

    @classmethod
    def from_env() -> "ApiConfig"
```

Gère la configuration d’accès à l’API (identifiants, URLs, timeouts).
