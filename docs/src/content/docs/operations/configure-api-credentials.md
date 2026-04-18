---
title: Configurer les clés API
description: Deux façons de fournir les identifiants PISTE au client.
sidebar:
  order: 4
---

Deux options — variables d'environnement (recommandé) ou `ApiConfig`
manuel.

## 1. Variables d'environnement (`.env`)

Créer un fichier `.env` à la racine du projet :

```bash
LEGIFRANCE_CLIENT_ID=votre_client_id
LEGIFRANCE_CLIENT_SECRET=votre_client_secret
```

Puis :

```python
from pylegifrance import LegifranceClient

client = LegifranceClient()    # lit .env via python-dotenv
```

:::caution
`.env` doit rester **hors de git** (`.gitignore`). Ne jamais logger
`client_secret`.
:::

## 2. Configuration manuelle

Utile si les clés viennent d'un vault ou d'un système externe :

```python
from pylegifrance import LegifranceClient
from pylegifrance.config import ApiConfig

client = LegifranceClient(
    ApiConfig(client_id="...", client_secret="...")
)
```

Les identifiants sont **obligatoires** dès l'instanciation ; sinon une
erreur est levée.

## Voir aussi

- [`/entities/api-config`](/pylegifrance/entities/api-config/)
- [`/concepts/piste-oauth`](/pylegifrance/concepts/piste-oauth/)
