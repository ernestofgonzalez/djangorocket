# End-to-end tests

These tests exercise the real product journey of Django Rocket: **run the
scaffolder → get a Django project → prove that project actually boots.**

## Suites

| File | What it does | Speed | When it runs |
| --- | --- | --- | --- |
| `test_scaffold.py` | Bakes the base template and asserts structure, slug rendering and that no `{{ cookiecutter.* }}` tokens survive. Only needs cookiecutter. | seconds | every `pytest` run |
| `test_add_command.py` | Regenerates every UI template zip from source, then drives the real `djangorocket add <component>` console script and asserts each template is written and fully rendered, without prompting, that it lands under `<templates dir>/components/ui/<name>/` (via `--templates-dir` and via `settings.py` discovery) and is includable at the path it documents, and that an unknown name fails non-zero. Runs on empty stdin, so any prompt the command grows back fails the suite. Only needs cookiecutter + the installed CLI. | seconds | every `pytest` run |
| `test_init_collision.py` | Drives the real `djangorocket init` and asserts project creation is collision-proof: the directory is kebab-cased and de-duplicated (`my-project`, `my-project-1`, …), two projects get disjoint compose project + volume names, and a name whose Docker volume already exists is skipped. Docker check skips when Docker is absent. | seconds | every `pytest` run |
| `test_init_collision.py` (`test_two_projects_run_postgres_and_redis_concurrently`) | Boots two generated projects' Postgres **and** Redis at the same time to prove `make bootstrap` is collision-proof: each gets free host ports (in `.env`, read by compose), a unique compose project and its own volumes, and a table written to one project's DB is invisible in the other's. Skips without a Docker daemon. | seconds | only with `--run-e2e` |
| `test_generated_project.py` | Builds a venv, installs the generated project's requirements, then runs `manage.py check`, `migrate` (SQLite) and `collectstatic`, and asserts migrations are in sync. | minutes | only with `--run-e2e` |
| `test_landing_page.py` | Renders the landing page of a booted project: once in-process via Django's test client, once by booting `runserver` and fetching `/` over HTTP. Asserts 200, the headline copy and the Tailwind stylesheet the `{% tailwind_css %}` inclusion tag emits. | minutes | only with `--run-e2e` |
| `test_generated_suite.py` | Runs the generated project's *own* pytest suite. | minutes | only with `--run-e2e` |
| `test_make_test.py` | Runs the generated project's `make test` target end to end and asserts it discovers and runs the bundled suite green. | minutes | only with `--run-e2e` |

## Running

```bash
make test        # fast: unit + scaffold tests (e2e skipped)
make test-e2e    # slow: pytest --run-e2e -m e2e
```

## Which Python the generated project is built with

`make bootstrap` builds a generated project's virtualenv with a bare
`python3 -m venv`, so the project runs on whatever interpreter the developer
happens to have installed -- in practice the newest one. These tests do the same:
`project_venv` picks the **newest** supported interpreter on `PATH`
(`SUPPORTED_PYTHONS` in `conftest.py`).

That matters. The suite used to prefer the *oldest* (3.10/3.11), which hid a
breakage for an entire Python release: Python 3.14 changed
`copy.copy(super())`, so Django 5.0's `BaseContext.__copy__` raised
`AttributeError: 'super' object has no attribute 'dicts'` and every page
rendering an inclusion tag -- the landing page included -- returned a 500, while
these tests stayed green on 3.10.

Override the choice with `DJANGOROCKET_E2E_PYTHON` (an interpreter name on `PATH`
or a full path). CI uses it to pin each end of the supported range to its own
matrix job:

```bash
DJANGOROCKET_E2E_PYTHON=python3.10 pytest --run-e2e -m e2e
```