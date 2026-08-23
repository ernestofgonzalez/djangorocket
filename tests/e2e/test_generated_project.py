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


def test_boots_without_aws_credentials(project_venv):
    """A fresh project must import settings and run manage.py with no AWS creds.

    ``settings.py`` builds the OpenSearch request signer only when credentials
    exist; without that guard ``AWSV4SignerAuth(None, ...)`` raises "Credentials
    cannot be empty" at import time, breaking every management command. This is
    exactly what ``make playground`` + ``make test`` hit, since the generated
    ``.env`` ships no AWS section.
    """
    # Drop the dummy AWS_* the fixture injects, and neutralise boto3's ambient
    # credential sources so the "no credentials" path is exercised on any host
    # (developer machine, CI role, etc.) rather than silently finding real keys.
    aws_keys = {
        "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
        "AWS_OPEN_SEARCH_REGION_NAME", "AWS_DEFAULT_REGION", "AWS_REGION",
        "AWS_PROFILE",
    }
    env = {k: v for k, v in project_venv.env.items() if k not in aws_keys}
    env["AWS_SHARED_CREDENTIALS_FILE"] = str(project_venv.project_dir / "no-such-aws-credentials")
    env["AWS_CONFIG_FILE"] = str(project_venv.project_dir / "no-such-aws-config")
    env["AWS_EC2_METADATA_DISABLED"] = "true"

    result = run(
        [project_venv.python, "src/manage.py", "check"],
        cwd=project_venv.project_dir,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stdout
    assert "System check identified no issues" in result.stdout


def test_boots_without_setuptools(project_venv, tmp_path):
    """A generated project must boot with no ``setuptools`` / ``pkg_resources``.

    Modern virtualenvs (Python 3.12+) no longer bundle ``setuptools``, which is
    what provides ``pkg_resources``. If any dependency does an unguarded
    ``import pkg_resources`` on a path the app actually exercises, ``make test``
    dies with ``ModuleNotFoundError: No module named 'pkg_resources'`` before a
    single assertion runs. ``django-countries`` did exactly this: resolving a URL
    imports the root URLconf -> ``billing.urls`` -> ``billing.views`` ->
    ``billing.forms`` -> ``django_countries.fields`` -> ``import pkg_resources``.

    ``manage.py check`` runs the URL system checks, so it imports that whole
    chain -- a fast, database-free proxy for the failing path. (Plain import or
    pytest collection misses it: nothing imports the URLconf until a request or a
    check forces it.) The builder interpreter (see ``_builder_python``) is often
    a 3.10/3.11 venv that still ships setuptools, so we don't rely on the host --
    a ``sitecustomize`` on ``PYTHONPATH`` hides ``pkg_resources`` at interpreter
    startup, before ``manage.py`` runs.
    """
    sitecustomize_dir = tmp_path / "no_setuptools"
    sitecustomize_dir.mkdir()
    (sitecustomize_dir / "sitecustomize.py").write_text(
        "import sys\nsys.modules['pkg_resources'] = None\n"
    )
    env = {**project_venv.env, "PYTHONPATH": str(sitecustomize_dir)}

    result = run(
        [project_venv.python, "src/manage.py", "check"],
        cwd=project_venv.project_dir,
        env=env,
        check=False,
    )
    assert "pkg_resources" not in result.stdout, result.stdout
    assert result.returncode == 0, result.stdout


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
