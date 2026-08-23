"""Fixtures and helpers for the end-to-end tests.

These exercise the real product journey: run the scaffolder -> get a Django
project -> prove that project actually boots. Because the generated project pins
heavy dependencies (``psycopg2``, ``boto3``, ``opensearch-py`` ...) we build a
dedicated virtualenv once per test session and reuse it across the e2e tests.
"""

import os
import shutil
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter

# tests/e2e/conftest.py -> repo root is two levels up.
REPO_ROOT = Path(__file__).resolve().parents[2]
BASE_TEMPLATE = REPO_ROOT / "djangorocket" / "templates" / "projects" / "base"

# Minimal environment needed to import the generated ``settings.py`` and run
# ``manage.py`` against a fresh scaffold. Several of these are *mandatory*:
# settings.py reads them at import time and crashes when they are missing
# (e.g. ``json.loads(os.environ["ALLOWED_HOSTS"])``), and the OpenSearch signer
# raises "Credentials cannot be empty" unless AWS_* are set. DATABASE_URL points
# at SQLite via dj-database-url so the tests need no running Postgres.
GENERATED_PROJECT_ENV = {
    "SECRET_KEY": "e2e-insecure-test-key",
    "DEBUG": "False",
    "ALLOWED_HOSTS": '["*"]',
    "CORS_ORIGIN_WHITELIST": "[]",
    "INTERNAL_IPS": "[]",
    "DATABASE_URL": "sqlite:///e2e.sqlite3",
    "SECURE_SSL_REDIRECT": "False",
    "AWS_ACCESS_KEY_ID": "testing",
    "AWS_SECRET_ACCESS_KEY": "testing",
    "AWS_OPEN_SEARCH_REGION_NAME": "us-east-1",
}

VenvProject = namedtuple("VenvProject", ["python", "project_dir", "env"])


def run(cmd, cwd, env=None, check=True):
    """Run a command, capturing combined output, and (optionally) assert success."""
    result = subprocess.run(
        [str(part) for part in cmd],
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            "command failed with exit code "
            f"{result.returncode}: {' '.join(str(part) for part in cmd)}\n\n"
            f"{result.stdout}"
        )
    return result


def bake(output_dir, extra_context=None):
    """Bake the base project template into ``output_dir``; return the project path."""
    project_dir = cookiecutter(
        str(BASE_TEMPLATE),
        no_input=True,
        output_dir=str(output_dir),
        extra_context=extra_context or {},
    )
    return Path(project_dir)


@pytest.fixture(scope="session")
def baked_project(tmp_path_factory):
    """A project baked once from the base template for the whole session."""
    output_dir = tmp_path_factory.mktemp("baked")
    return bake(output_dir)


def _builder_python():
    """Pick an interpreter to install the generated project's deps into.

    The generated project targets Python 3.10 (see its ``runtime.txt``) and pins
    2022-era dependencies (Django 5.0, etc.), so prefer a 3.10/3.11 interpreter
    on PATH to match what the scaffold actually supports, then fall back to the
    interpreter running the tests when it is itself 3.11 or older. Returns
    ``None`` if nothing suitable is available (the fixtures then skip).

    Note: ``requirements.txt`` pins the source ``psycopg2`` (no wheels), so the
    chosen interpreter's environment must have ``pg_config`` (libpq) on PATH to
    build it. The ``psycopg2==2.9.10`` pin itself builds fine on modern CPython.
    """
    for name in ("python3.10", "python3.11"):
        found = shutil.which(name)
        if found:
            return found
    if sys.version_info < (3, 12):
        return sys.executable
    return None


@pytest.fixture(scope="session")
def project_venv(baked_project, tmp_path_factory):
    """A virtualenv with the generated project's requirements installed.

    Built once per session (installing ~40 packages, incl. compiling psycopg2).
    """
    builder = _builder_python()
    if builder is None:
        pytest.skip(
            "e2e needs a Python 3.10-3.12 interpreter to build the generated "
            "project's pinned psycopg2==2.9.3 (none found on PATH)."
        )

    venv_dir = tmp_path_factory.mktemp("venv")
    subprocess.run([builder, "-m", "venv", str(venv_dir)], check=True)

    bin_dir = venv_dir / ("Scripts" if os.name == "nt" else "bin")
    python = bin_dir / "python"

    run([python, "-m", "pip", "install", "--upgrade", "pip", "wheel"], cwd=baked_project)
    for req in ("requirements.txt", "requirements-testing.txt"):
        run(
            [python, "-m", "pip", "install", "-r", baked_project / "requirements" / req],
            cwd=baked_project,
        )

    env = {**os.environ, **GENERATED_PROJECT_ENV}
    env.pop("PYTHONPATH", None)  # don't leak the outer env into the inner venv
    return VenvProject(python=python, project_dir=baked_project, env=env)
