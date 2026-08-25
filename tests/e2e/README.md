# End-to-end tests

These tests exercise the real product journey of Django Rocket: **run the
scaffolder → get a Django project → prove that project actually boots.**

## Suites

| File | What it does | Speed | When it runs |
| --- | --- | --- | --- |
| `test_scaffold.py` | Bakes the base template and asserts structure, slug rendering and that no `{{ cookiecutter.* }}` tokens survive. Only needs cookiecutter. | seconds | every `pytest` run |
| `test_add_command.py` | Regenerates `accordion.zip` from source, then drives the real `djangorocket add accordion` console script and asserts the UI template is written and fully rendered. Only needs cookiecutter + the installed CLI. | seconds | every `pytest` run |
| `test_init_collision.py` | Drives the real `djangorocket init` and asserts project creation is collision-proof: the directory is kebab-cased and de-duplicated (`my-project`, `my-project-1`, …), two projects get disjoint compose project + volume names, and a name whose Docker volume already exists is skipped. Docker check skips when Docker is absent. | seconds | every `pytest` run |
| `test_init_collision.py` (`test_two_projects_run_postgres_and_redis_concurrently`) | Boots two generated projects' Postgres **and** Redis at the same time to prove `make bootstrap` is collision-proof: each gets free host ports (in `.env`, read by compose), a unique compose project and its own volumes, and a table written to one project's DB is invisible in the other's. Skips without a Docker daemon. | seconds | only with `--run-e2e` |
| `test_generated_project.py` | Builds a venv, installs the generated project's requirements, then runs `manage.py check`, `migrate` (SQLite) and `collectstatic`, and asserts migrations are in sync. | minutes | only with `--run-e2e` |
| `test_generated_suite.py` | Runs the generated project's *own* pytest suite. | minutes | only with `--run-e2e` |
| `test_make_test.py` | Runs the generated project's `make test` target end to end and asserts it discovers and runs the bundled suite green. | minutes | only with `--run-e2e` |

## Running

```bash
make test        # fast: unit + scaffold tests (e2e skipped)
make test-e2e    # slow: pytest --run-e2e -m e2e
```