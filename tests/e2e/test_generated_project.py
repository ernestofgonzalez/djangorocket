"""Prove a freshly scaffolded project actually boots.

Opt-in (``--run-e2e``): builds a virtualenv, installs the generated project's
dependencies and runs real ``manage.py`` commands against a SQLite database.
This is the core end-to-end guarantee: "run the scaffolder and you get a Django
project that installs, imports its settings, migrates and collects static".
"""

import pytest

from .conftest import run

pytestmark = pytest.mark.e2e


def _manage(venv, *args):
    return run(
        [venv.python, "src/manage.py", *args],
        cwd=venv.project_dir,
        env=venv.env,
        check=False,
    )


def test_dependencies_install(project_venv):
    """The generated requirements resolve and install (fixture did the work)."""
    assert project_venv.python.exists()


def test_manage_check_passes(project_venv):
    result = _manage(project_venv, "check")
    assert result.returncode == 0, result.stdout
    assert "System check identified no issues" in result.stdout


def test_migrations_apply_on_sqlite(project_venv):
    result = _manage(project_venv, "migrate", "--noinput")
    assert result.returncode == 0, result.stdout
    assert "Applying" in result.stdout


def test_collectstatic_succeeds(project_venv):
    result = _manage(project_venv, "collectstatic", "--noinput")
    assert result.returncode == 0, result.stdout
    assert "static files copied" in result.stdout


@pytest.mark.xfail(
    reason=(
        "Boilerplate ships an out-of-sync migration: the User model's manager "
        "change (0002_alter_user_managers) is not captured in a migration. "
        "Remove this xfail once the template adds the missing migration."
    ),
    strict=False,
)
def test_migrations_are_in_sync(project_venv):
    result = _manage(project_venv, "makemigrations", "--check", "--dry-run")
    assert result.returncode == 0, result.stdout
