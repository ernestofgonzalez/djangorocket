# End-to-end tests

These tests exercise the real product journey of Django Rocket: **run the
scaffolder → get a Django project → prove that project actually boots.**

## Suites

| File | What it does | Speed | When it runs |
| --- | --- | --- | --- |
| `test_scaffold.py` | Bakes the base template and asserts structure, slug rendering and that no `{{ cookiecutter.* }}` tokens survive. Only needs cookiecutter. | seconds | every `pytest` run |
| `test_generated_project.py` | Builds a venv, installs the generated project's requirements, then runs `manage.py check`, `migrate` (SQLite) and `collectstatic`. | minutes | only with `--run-e2e` |
| `test_generated_suite.py` | Runs the generated project's *own* pytest suite. | minutes | only with `--run-e2e` |

## Running

```bash
make test        # fast: unit + scaffold tests (e2e skipped)
make test-e2e    # slow: pytest --run-e2e -m e2e
```