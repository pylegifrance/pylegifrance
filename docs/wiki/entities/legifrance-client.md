---
title: LegifranceClient
description: Client HTTP qui encapsule l'authentification OAuth PISTE et les appels à l'API Legifrance.
sidebar:
  order: 1
---

`LegifranceClient` est le point d'entrée unique pour tous les appels à l'API
Legifrance. Il encapsule :

- la configuration ([`ApiConfig`](/pylegifrance/entities/api-config/)) ;
- l'authentification OAuth PISTE ([voir `concepts/piste-oauth`](/pylegifrance/concepts/piste-oauth/)) ;
- une `requests.Session` avec gestion des timeouts ;
- les méthodes `call_api`, `get`, `ping`.

## Construire un client

Deux façons :

```python
from pylegifrance import LegifranceClient

# 1. Depuis l'environnement (LEGIFRANCE_CLIENT_ID / _SECRET dans .env)
client = LegifranceClient()

# 2. Manuellement, avec un ApiConfig explicite
from pylegifrance.config import ApiConfig

client = LegifranceClient(
    ApiConfig(client_id="...", client_secret="...")
)
```

Les identifiants sont obligatoires ; sinon une erreur est levée à
l'instanciation.

## Cycle de vie

```python
with client.session_context():
    ...  # appels API
```

Le contexte ferme proprement la session à la sortie.

## Méthodes

| Méthode | Rôle |
|---|---|
| `call_api(route, data)` | POST JSON vers `route` |
| `get(route)` | GET vers `route` |
| `ping(route="consult/ping")` | Vérifie l'accès à l'API |
| `update_api_keys(...)` | Change les identifiants à chaud |

Pour la signature complète, voir [`/references/client`](/pylegifrance/references/client/).

## Voir aussi

- [`ApiConfig`](/pylegifrance/entities/api-config/) — forme de la config passée au client.
- [`Authentication`](/pylegifrance/entities/authentication/) — ce qui se passe avant chaque appel.
- [`Fond Code`](/pylegifrance/entities/fond-code/), [`Fond Juri`](/pylegifrance/entities/fond-juri/),
  [`Fond LODA`](/pylegifrance/entities/fond-loda/) — façades qui consomment le client.
