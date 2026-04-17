# Guide de Contribution

Merci de votre intérêt pour ce projet ! Ce guide a pour but de garantir une collaboration efficace et cohérente.

## Technologies utilisées

Ce projet s'appuie sur les technologies suivantes :
- [**Python**](https://www.python.org/) comme langage principal
- [**UV**](https://github.com/astral-sh/uv) comme gestionnaire de paquets
- [**pre-commit**](https://pre-commit.com/) pour l'assurance qualité du code
- Le [**développement piloté par le comportement (BDD)**](https://behave.readthedocs.io/en/latest/) avec la syntaxe [**Cucumber**](https://cucumber.io/)

## Étapes pour contribuer

### 1. Ouvrir ou identifier une *issue*

- Vérifiez qu’une [issue](../../issues) existe pour le problème ou la fonctionnalité.
- Sinon, ouvrez une nouvelle issue en suivant le modèle proposé.

### 2. Créer une branche depuis GitHub

- Depuis l’issue, cliquez sur **"Create branch"** dans l’interface GitHub.
- Cela crée automatiquement une branche nommée selon l’issue et la lie à celle-ci.

> ⚠️ N'utilisez **pas** `main` ou `develop` pour vos modifications.

## Transparence LLM pour les demandes de fonctionnalité

Si vous avez utilisé un LLM (ChatGPT, Claude, Codex, etc.) pour rédiger ou affiner votre demande de fonctionnalité, **incluez le prompt utilisé, verbatim**, dans le champ « Prompt LLM utilisé » de l'issue (ou collez-le dans « Informations Complémentaires » si votre éditeur ne le montre pas).

Cela sert deux objectifs :

1. **Transparence** — les mainteneurs voient l'intention brute derrière la proposition, avant reformulation.
2. **Matière première du wiki** — ces prompts sont archivés dans `docs/raw/prompts/` et servent de sources pour maintenir la documentation (voir `docs/CLAUDE.md`).

Vous n'êtes pas obligé·e d'utiliser un LLM. Mais si vous l'avez fait, partagez-le plutôt que de le cacher.

## Préparer votre environnement

### 1. Installer les dépendances avec UV

Assurez-vous que [UV](https://github.com/astral-sh/uv) est installé, puis synchronisez l'environnement :

```bash
  uv sync --all-extras
```

Cette commande installe toutes les dépendances de base et optionnelles.

### 2. Configurer les hooks pre-commit

```bash
  uv run pre-commit install
  uv run pre-commit run --all-files
```

## Ouvrir une Pull Request

### 1. Pousser votre branche

Poussez votre branche sur GitHub :

```bash
  git push origin <nom-de-branche>
```

### 2. Créer la Pull Request

Créez une [Pull Request](https://docs.github.com/fr/pull-requests) depuis l'interface GitHub.

## Bonnes pratiques

- Une PR = une fonctionnalité ou un correctif
- Assurez-vous que tout le code est en anglais, mais que les messages de log sont en français
- Suivez les standards de codage décrits ci-dessous

---

# Standards de Codage pour PyLegifrance

Ce document présente les standards et conventions de codage à suivre lors de contributions au projet PyLegifrance. Ces standards assurent la cohérence, la lisibilité et la maintenabilité du code.

## Directives Linguistiques

### Règles Générales de Langage

- **Code (identifiants, commentaires, docstrings)** : Tout le code doit être écrit en **anglais**.
- **Messages de Log** : Tous les messages de log doivent être écrits en **français**.

### Exemples

#### Exemple de Code Correct :

```python
def search_article(article_id):
    """
    Search for an article by its ID.

    Args:
        article_id (str): The ID of the article to search for.

    Returns:
        dict: The article data if found, None otherwise.
    """
    logger.info(f"Recherche de l'article avec l'identifiant {article_id}")
    # Implementation...
```

#### Exemple de Code Incorrect :

```python
def recherche_article(article_id):
    """
    Recherche un article par son identifiant.

    Args:
        article_id (str): L'identifiant de l'article à rechercher.

    Returns:
        dict: Les données de l'article si trouvé, None sinon.
    """
    logger.info(f"Searching for article with ID {article_id}")
    # Implementation...
```

## Conventions de Nommage

### Fichiers et Modules

- Utilisez des minuscules avec des tirets bas pour les noms de fichiers et de modules : `search_utils.py`, `api_client.py`
- Exception : Lorsqu'un fichier contient une seule classe, le nom du fichier doit correspondre au nom de la classe (en snake_case) : `legifrance_client.py` pour la classe `LegifranceClient`

### Classes

- Utilisez CapWords (PascalCase) pour les noms de classes : `LegifranceClient`, `SearchResponse`
- Exception : Les acronymes doivent être en majuscules : `JSONParser`, `APIClient`

### Fonctions et Méthodes

- Utilisez des minuscules avec des tirets bas (snake_case) : `search_code()`, `get_article_id()`
- Les méthodes privées doivent commencer par un seul tiret bas : `_call_api_single()`

### Variables

- Utilisez des minuscules avec des tirets bas (snake_case) : `article_id`, `search_result`
- Les constantes doivent être en MAJUSCULES_AVEC_TIRETS_BAS : `MAX_RESULTS`, `DEFAULT_TIMEOUT`
- Les variables privées doivent commencer par un seul tiret bas : `_client`

### Annotations de Type

- Utilisez toujours des annotations de type pour les paramètres de fonction et les valeurs de retour
- Utilisez `Optional[Type]` pour les paramètres qui peuvent être None
- Utilisez `Union[Type1, Type2]` pour les paramètres qui peuvent être de plusieurs types

## Terminologie Spécifique au Domaine

### Termes Juridiques

- Les termes juridiques français doivent être conservés dans leur forme originale lorsqu'ils représentent des concepts spécifiques du système juridique français :
  - `LODA` (Lois, Ordonnances, Décrets, Arrêtés)
  - `JURI` (Jurisprudence)
  - `LEGITEXT`, `LEGIARTI` (identifiants spécifiques à Legifrance)

### Enums

- Les noms de classes Enum doivent suivre la convention de nommage des classes (PascalCase)
- Les valeurs d'Enum doivent être en MAJUSCULES : `TypeRecherche.EXACTE`, `Operateur.ET`

## Documentation

### Docstrings

- Utilisez des triples guillemets doubles (`"""`) pour les docstrings
- Suivez le format de docstring Google :
  ```python
  def function(param1, param2):
      """Short description.

      Longer description if needed.

      Args:
          param1 (type): Description of param1.
          param2 (type): Description of param2.

      Returns:
          type: Description of return value.

      Raises:
          ExceptionType: When and why this exception is raised.
      """
  ```

### Commentaires

- Utilisez les commentaires avec parcimonie et uniquement lorsque nécessaire pour expliquer une logique complexe
- Les commentaires doivent expliquer "pourquoi" plutôt que "quoi" (le code doit être auto-explicatif)
- Maintenez les commentaires à jour lors de la modification du code

## Journalisation (Logging)

### Niveaux de Log

- `DEBUG` : Informations détaillées, généralement utiles uniquement pour diagnostiquer des problèmes
- `INFO` : Confirmation que les choses fonctionnent comme prévu
- `WARNING` : Indication que quelque chose d'inattendu s'est produit, mais l'application fonctionne toujours
- `ERROR` : En raison d'un problème plus grave, l'application n'a pas pu exécuter une fonction
- `CRITICAL` : Une erreur grave indiquant que le programme lui-même pourrait ne pas pouvoir continuer à s'exécuter

### Format des Messages de Log

- Tous les messages de log doivent être en **français**
- Incluez le contexte pertinent dans les messages de log (par exemple, IDs, codes de statut)
- Pour les logs de débogage, incluez des informations détaillées utiles pour le dépannage
- Exemple :
```python
logger.info(f"Démarrage de la recherche avec les paramètres: {params}")
logger.warning(f"Échec de la connexion à l'API, nouvelle tentative ({retry_count}/3)")
logger.error(f"Impossible de récupérer l'article {article_id}: {error}")
```

## Organisation du Code

### Imports

- Groupez les imports dans l'ordre suivant, séparés par une ligne vide :
  1. Imports de la bibliothèque standard
  2. Imports tiers associés
  3. Imports spécifiques à l'application/bibliothèque locale
- Au sein de chaque groupe, les imports doivent être triés par ordre alphabétique  
- Exemple :
```python
import json
import logging
from typing import Dict, List, Optional, Union

from pydantic import BaseModel
import requests

from pylegifrance.models.constants import Fonds, TypeRecherche
from pylegifrance.utils.formatters import format_response
```

### Structure de Classe

- Organisez le contenu des classes comme suit :
  1. Attributs de classe et constantes
  2. Méthode `__init__`
  3. Méthodes publiques
  4. Méthodes privées (préfixées par `_`)
  5. Méthodes statiques et de classe
  6. Propriétés
  7. Méthodes spéciales (`__str__`, `__repr__`, etc.)

## Gestion des Erreurs

- Utilisez des types d'exception spécifiques plutôt que d'attraper toutes les exceptions
- Incluez toujours des messages d'erreur significatifs
- Journalisez les exceptions avec un contexte approprié
- Exemple :
```python
try:
    response = self.client.call_api(route, data)
except ConnectionError as e:
    logger.error(f"Erreur de connexion lors de l'appel à {route}: {str(e)}")
    raise APIConnectionError(f"Failed to connect to API: {str(e)}")
except TimeoutError as e:
    logger.error(f"Délai d'attente dépassé lors de l'appel à {route}: {str(e)}")
    raise APITimeoutError(f"API call timed out: {str(e)}")
```

## Conclusion

Le respect de ces standards de codage garantira que le code de PyLegifrance reste cohérent, lisible et maintenable. Ces standards sont basés sur les modèles existants trouvés dans la documentation et le code du projet.

### Rappel des points essentiels
- Code (identifiants, commentaires, docstrings) en **anglais**
- Messages de log en **français**
- Conventions de nommage cohérentes
- Documentation complète
- Gestion appropriée des erreurs
