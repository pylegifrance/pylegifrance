# Référence API

Cette section contient la documentation technique détaillée de la bibliothèque PyLegifrance. Elle est organisée par catégories pour faciliter la navigation et la recherche d'informations.

## Client et Configuration

Ces classes permettent d'initialiser et de configurer l'accès à l'API Legifrance.

- [LegifranceClient](classes/legifrance_client.md) - Client principal pour interagir avec l'API Legifrance
- [ApiConfig](classes/api_config.md) - Configuration d'accès à l'API (identifiants, URLs, timeouts)

## Recherche et Consultation

Ces fonctions permettent d'effectuer des recherches dans les différentes bases de données juridiques.

### Codes

- [Code](Fond/recherche_code.md) - Recherche dans les codes français (Code civil, Code pénal, etc.) avec une API fluide

### Lois, Ordonnances, Décrets et Arrêtés (LODA)

- [Loda](fonctions/recherche_loda.md) - Recherche dans les lois, ordonnances, décrets et arrêtés

### Jurisprudence

- [JuriAPI](Fond/juri_api.md) - API pour récupérer et rechercher des décisions de jurisprudence
- [JuriDecision](classes/juri_decision.md) - Représentation d'une décision de jurisprudence
