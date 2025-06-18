# JURI

```python
class JuriAPI:
    def __init__(self, client: LegifranceClient)
    def fetch(self, text_id: str) -> JuriDecision
    def fetch_with_ancien_id(self, ancien_id: str) -> JuriDecision
    def fetch_version_at(self, text_id: str, date: str) -> JuriDecision
    def fetch_versions(self, text_id: str) -> List[JuriDecision]
    def search(self, query: Union[str, SearchRequest]) -> List[JuriDecision]
```

Fournit des méthodes pour récupérer et rechercher des décisions de jurisprudence.