# Testing

> Every convention below cites the official documentation that grounds
> it. **Read the linked source before modifying any rule here.**

## Directory Structure

> Sources:
>
> - [pytest — Good integration practices (test layout)](https://docs.pytest.org/en/stable/explanation/goodpractices.html).
> - [pytest — `conftest.py` scoping](https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files).

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

> Sources:
>
> - [pytest-bdd — Main docs](https://pytest-bdd.readthedocs.io/en/stable/).
> - [pytest-bdd — `scenarios()` loader](https://pytest-bdd.readthedocs.io/en/stable/#scenarios-shortcut).
> - [pytest-bdd — Reusing steps](https://pytest-bdd.readthedocs.io/en/stable/#reusing-fixtures-and-steps).
> - [Cucumber — Gherkin reference](https://cucumber.io/docs/gherkin/reference/)
>   (specifically the `# language: fr` header).

Feature files are written in **French** (`# language: fr`).

Step definitions live in `steps.py` next to the `.feature` file. Shared
steps (e.g. "l'API Legifrance est accessible") live in
`tests/integration/fonds/shared.py`.

Scenario runners follow this exact template:

```python
# ruff: noqa: F403
from pytest_bdd import scenarios

from tests.integration.fonds.<fond>.steps import *
from tests.integration.fonds.shared import *

scenarios("<fond>.feature")
```

The `# ruff: noqa: F403` directive is required for wildcard imports in
scenario runners.

## Fixtures

> Sources:
>
> - [pytest — Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html).
> - [pytest — Fixture scopes](https://docs.pytest.org/en/stable/how-to/fixtures.html#fixture-scopes).

- `api_client` (module scope): Creates a real `LegifranceClient` from
  env vars. Defined in `tests/conftest.py`.
- Integration tests require valid `.env` credentials.

## Adding a New Fond

> Project-specific workflow — see the wiki for fond-level walkthroughs:
> [`docs/src/content/docs/operations/`](../../docs/src/content/docs/operations/).

1. Create `tests/integration/fonds/<fond>/` with `<fond>.feature`,
   `steps.py`, `test_<fond>_scenario.py`.
2. Write scenarios in French matching the Gherkin `# language: fr`
   header.
3. Reuse shared steps from `shared.py` via wildcard import.
4. Add fond-specific step definitions in the local `steps.py`.
