# Testing

## Directory Structure

```
tests/
  conftest.py              # Shared fixtures (api_client at module scope)
  unit/
    fonds/                 # Unit tests per fond
  integration/
    fonds/
      shared.py            # Shared BDD step definitions
      code/
        code.feature       # Gherkin scenarios (French)
        steps.py           # Step implementations
        test_code_scenario.py  # Scenario runner
      juri/                # Same structure
      loda/                # Same structure
```

## pytest-bdd Pattern

Feature files are written in **French** (`# language: fr`).

Step definitions live in `steps.py` next to the `.feature` file. Shared steps (e.g. "l'API Legifrance est accessible") live in `tests/integration/fonds/shared.py`.

Scenario runners follow this exact template:

```python
# ruff: noqa: F403
from pytest_bdd import scenarios

from tests.integration.fonds.<fond>.steps import *
from tests.integration.fonds.shared import *

scenarios("<fond>.feature")
```

The `# ruff: noqa: F403` directive is required for wildcard imports in scenario runners.

## Fixtures

- `api_client` (module scope): Creates a real `LegifranceClient` from env vars. Defined in `tests/conftest.py`.
- Integration tests require valid `.env` credentials.

## Adding a New Fond

1. Create `tests/integration/fonds/<fond>/` with `<fond>.feature`, `steps.py`, `test_<fond>_scenario.py`.
2. Write scenarios in French matching the Gherkin `# language: fr` header.
3. Reuse shared steps from `shared.py` via wildcard import.
4. Add fond-specific step definitions in the local `steps.py`.
