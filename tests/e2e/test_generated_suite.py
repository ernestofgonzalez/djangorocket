"""Run the generated project's OWN test suite.

Opt-in (``--run-e2e``). This proves a scaffolded project runs its bundled tests
green from a clean bake: settings detect the test run and skip the build-step
machinery (the hashed staticfiles manifest and offline-compressed assets), and
the register view no longer calls Stripe when no key is configured, so no manual
setup is required.

``test_generated_suite_is_collectable`` additionally guards that the harness is
wired correctly (tests are collected and a meaningful number pass), catching
regressions in the scaffold itself even if the green assertion is relaxed.
"""

import re

import pytest

from .conftest import run

pytestmark = pytest.mark.e2e


def _run_generated_suite(venv):
    # The bundled suite renders templates, so build the static + compressor
    # artifacts it expects first (best effort; compress warns but exits 0).
    run(
        [venv.python, "src/manage.py", "collectstatic", "--noinput"],
        cwd=venv.project_dir,
        env=venv.env,
        check=False,
    )
    run(
        [venv.python, "src/manage.py", "compress", "--force"],
        cwd=venv.project_dir,
        env=venv.env,
        check=False,
    )
    return run(
        [venv.python, "-m", "pytest", "-p", "no:cacheprovider", "-q"],
        cwd=venv.project_dir,
        env=venv.env,
        check=False,
    )


def _counts(output):
    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", output)) else 0
    failed = int(m.group(1)) if (m := re.search(r"(\d+) failed", output)) else 0
    return passed, failed


def test_generated_suite_is_collectable(project_venv):
    """The scaffold wires pytest correctly: tests are found and some pass."""
    result = _run_generated_suite(project_venv)
    passed, failed = _counts(result.stdout)
    assert passed + failed > 0, f"no tests ran:\n{result.stdout}"
    assert passed > 0, f"expected some passing tests:\n{result.stdout}"


def test_generated_suite_is_green(project_venv):
    result = _run_generated_suite(project_venv)
    _passed, failed = _counts(result.stdout)
    assert result.returncode == 0 and failed == 0, result.stdout
