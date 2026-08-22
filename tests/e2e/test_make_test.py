"""Run the generated project's ``make test`` target end to end.

Opt-in (``--run-e2e``). ``make test`` is a primary entry point a developer hits
right after scaffolding: it invokes Django's own test runner
(``cd src && python3 manage.py test``). Exercising it proves the whole chain
works from a clean bake -- dependencies install (notably the pinned
``psycopg2``, compiled from source), ``settings.py`` imports, the app registry
loads, and Django *discovers and runs* the bundled tests. That is a different
code path from the pytest-based ``test_generated_suite.py`` and would have
caught, for example, a ``psycopg2`` build failure (project fails to import) or
the discovery regression this target had (tests run from the repo root, where
``src/`` is not a package, find nothing).
"""

import os
import re
import shutil

import pytest

from .conftest import run

pytestmark = pytest.mark.e2e


def _venv_env(venv):
    """``venv.env`` with the venv's bin dir first on PATH.

    The generated ``Makefile`` hardcodes ``python3``; prepending the venv bin
    dir makes that resolve to the project's interpreter (with its installed
    dependencies) instead of the system one, so ``make test`` runs against the
    freshly built virtualenv.
    """
    bin_dir = os.path.dirname(str(venv.python))
    env = dict(venv.env)
    env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
    return env


def _run_make_test(venv):
    if shutil.which("make") is None:
        pytest.skip("`make` is not available on PATH")
    return run(["make", "test"], cwd=venv.project_dir, env=_venv_env(venv), check=False)


def _counts(output):
    """Parse Django's test-runner summary from combined stdout/stderr."""

    def _int(pattern):
        m = re.search(pattern, output)
        return int(m.group(1)) if m else 0

    found = _int(r"Found (\d+) test")
    ran = _int(r"Ran (\d+) test")
    failures = _int(r"failures=(\d+)")
    errors = _int(r"errors=(\d+)")
    return found, ran, failures, errors


def test_make_test_discovers_and_runs_suite(project_venv):
    """``make test`` discovers the bundled suite and actually runs it green-ish.

    The core guarantee: Django finds the project's tests (the target runs from
    ``src/``) and a meaningful number execute and pass -- which only happens if
    the dependency install, settings import and app loading all succeeded.
    """
    result = _run_make_test(project_venv)
    found, ran, failures, errors = _counts(result.stdout)
    # Discovery works: the runner found the bundled tests (regression guard --
    # this was 0 when the target ran from the repo root).
    assert found > 0, result.stdout
    assert ran > 0, result.stdout
    # Some tests genuinely passed, proving the project booted end to end.
    assert ran - failures - errors > 0, result.stdout


@pytest.mark.xfail(
    reason=(
        "The bundled suite is not fully green from a clean bake: templates need "
        "collectstatic/compress artifacts (Missing staticfiles manifest entry), "
        "the register view calls Stripe without a key, and billing_settings.html "
        "uses a |div filter django-compressor rejects. Remove this xfail once "
        "`make test` runs the template's tests green."
    ),
    strict=False,
)
def test_make_test_is_green(project_venv):
    result = _run_make_test(project_venv)
    _found, _ran, failures, errors = _counts(result.stdout)
    assert result.returncode == 0 and failures == 0 and errors == 0, result.stdout
