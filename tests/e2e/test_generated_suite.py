"""Run the generated project's OWN test suite.

Opt-in (``--run-e2e``). This documents whether a scaffolded project can run
its bundled tests green from a clean bake. Today it cannot, for reasons that are
genuine template issues rather than test-harness problems:

  * the register view calls Stripe, which raises ``AuthenticationError`` without
    a (test) API key -- the suite needs Stripe stubbing/keys;
  * ``COMPRESS_OFFLINE`` templates need ``manage.py compress`` to have built an
    offline manifest, and ``billing_settings.html`` uses an ``|div`` filter that
    django-compressor rejects.

So the "suite is fully green" assertion is marked xfail(strict=False): it will
flip to XPASS -- a signal to tighten this test -- once the template is fixed. We
still assert here that the harness is wired correctly (tests are collected and a
meaningful number pass), which guards against regressions in the scaffold itself.
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


@pytest.mark.xfail(
    reason="Generated suite has known failures (Stripe not stubbed; compressor "
    "offline/|div filter). Remove this xfail once the template is fixed.",
    strict=False,
)
def test_generated_suite_is_green(project_venv):
    result = _run_generated_suite(project_venv)
    _passed, failed = _counts(result.stdout)
    assert result.returncode == 0 and failed == 0, result.stdout
