---
title: Architecture
description: Architecture en couches User → Façade → Modèles → Client → API.
sidebar:
  order: 1
---

Architecture en couches :

```
User → fonds/ (façades) → models/ (domaine) → models/generated/ → client.py → API Legifrance
```

1. **Façades de domaine** (`fonds/`) — API de haut niveau par fond documentaire
   (`Code`, `JuriAPI`, `Loda`).
2. **Modèles de domaine** (`models/<fond>/`) — structures métier validées par
   Pydantic (recherche, consultation, résultats).
3. **Modèles générés** (`models/generated/`) — modèles auto-générés depuis
   le schéma OpenAPI de Legifrance. Voir
   [`/concepts/generated-models`](/pylegifrance/concepts/generated-models/).
4. **Client API** (`client.py`) — communication HTTPS/JSON, auth, timeouts.

## Pourquoi cette séparation ?

L'enjeu est de **séparer l'interface utilisateur de la logique technique**.

- **`fonds/`** : façade de domaine
  - API stable et intuitive pour développeur·se·s et juristes.
  - Masque la complexité de l'API Legifrance.
  - Fournit des objets métier enrichis.
  - Protège le code client des changements dans l'API sous-jacente.

- **`models/`** : modèles de données
  - Structure précise des données juridiques.
  - Validation via Pydantic (typage fort, contraintes).
  - Conversion bidirectionnelle avec les modèles d'API.
  - Organisation par préoccupation technique.

Voir [`/concepts/fond-facade`](/pylegifrance/concepts/fond-facade/) pour le raisonnement
détaillé.

## Flux de données

```mermaid
flowchart TD
    dev[Développeur·se]
    facade[Façade fonds/*]
    models[Modèles models/*]
    gen[Modèles générés]
    client[LegifranceClient]
    api[API Legifrance]

    dev -->|1. Appelle| facade
    facade -->|2. Utilise| models
    models -->|3. to_generated()| gen
    gen -->|4. Payload JSON| client
    client -->|5. HTTPS| api

    api -->|6. Réponse| client
    client -->|7. Transmet| gen
    gen -->|8. from_generated()| models
    models -->|9. Traitement| facade
    facade -->|10. Objets enrichis| dev

    classDef external fill:#999,stroke:#333,stroke-width:2px
    classDef core fill:#9cf,stroke:#333,stroke-width:2px

    class dev,api external
    class facade,models,gen,client core
```

## Diagrammes C4

Les diagrammes C4 (contexte, conteneurs, composants) sont décrits en source
PlantUML dans l'ancienne doc MkDocs et dans
[`raw/legifrance/`](https://github.com/pylegifrance/pylegifrance/tree/main/docs/raw)
(en attente de pré-rendu SVG pour rendu natif dans Starlight).

## Avantages clés

- **Stabilité** : interface publique indépendante des changements d'API.
- **Modèles métier** : fonctionnalités spécifiques au domaine juridique.
- **Validation robuste** : typage et validation Pydantic.
- **Structure intuitive** : organisation par fond documentaire.

## Voir aussi

- [`/concepts/builder-pattern`](/pylegifrance/concepts/builder-pattern/)
- [`/concepts/fond-facade`](/pylegifrance/concepts/fond-facade/)
- [`/concepts/generated-models`](/pylegifrance/concepts/generated-models/)
