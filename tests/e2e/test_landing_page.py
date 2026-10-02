"""Prove the landing page actually renders.
"""

import contextlib
import socket
import subprocess
import time
import urllib.error
import urllib.request

import pytest

from .conftest import run

pytestmark = pytest.mark.e2e

# Copy from src/templates/pages/index.html, and the stylesheet that only appears
# when the {% tailwind_css %} inclusion tag inside {% compress css %} rendered.
LANDING_HEADLINE = "Your project is live."
TAILWIND_STYLESHEET = "css/dist/styles.css"

# Fetch the page in-process through Django's test client. ``manage.py shell -c``
# gets settings, sys.path and the app registry set up exactly as the project
# does, so this needs no port and no server. The client re-raises view
# exceptions, so a template error fails the command with its real traceback
# instead of a bare 500.
RENDER_SCRIPT = """
from django.test import Client

response = Client().get("/", HTTP_HOST="127.0.0.1")
print("STATUS:", response.status_code)
print(response.content.decode("utf-8", "replace"))
"""


def _debug_env(venv):
    """``venv.env`` with ``DEBUG=True``, as ``make runserver`` runs the project.

    The generated ``.env`` ships ``DEBUG=True``; the shared fixture env uses
    ``DEBUG=False`` so that the other e2e tests exercise production settings.
    """
    return {**venv.env, "DEBUG": "True"}


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextlib.contextmanager
def _runserver(venv, port):
    """Run the development server on ``port`` until the block exits.

    ``--noreload`` keeps it to a single process: the autoreloader would fork a
    child that outlives ``terminate()`` and keep the port bound.
    """
    process = subprocess.Popen(
        [str(venv.python), "manage.py", "runserver", "--noreload", str(port)],
        cwd=str(venv.project_dir / "src"),
        env=_debug_env(venv),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        yield process
    finally:
        process.terminate()
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=30)


def _get_until_up(process, url, timeout=60):
    """GET ``url`` once the server answers; fail if it never does."""
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise AssertionError(
                "runserver exited with code {0} before answering:\n\n{1}".format(
                    process.returncode, process.stdout.read()
                )
            )
        try:
            # A 500 comes back as HTTPError; return it so the test can assert on
            # the status and body rather than timing out.
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.status, response.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as error:
            return error.code, error.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as error:
            last_error = error
            time.sleep(0.5)
    raise AssertionError(
        "runserver never answered on {0} within {1}s (last error: {2})".format(
            url, timeout, last_error
        )
    )


def test_landing_page_renders(project_venv):
    """GET / renders the landing page instead of raising from the template.

    Runs in-process, so a regression reports the template traceback itself --
    the precise failure, not just a status code.
    """
    result = run(
        [project_venv.python, "src/manage.py", "shell", "-c", RENDER_SCRIPT],
        cwd=project_venv.project_dir,
        env=_debug_env(project_venv),
        check=False,
    )
    assert result.returncode == 0, result.stdout
    assert "STATUS: 200" in result.stdout, result.stdout
    assert LANDING_HEADLINE in result.stdout, result.stdout
    # The inclusion tag inside {% compress css %} rendered: this is the exact
    # path Python 3.14 broke, and it stays silent in a status-code-only check.
    assert TAILWIND_STYLESHEET in result.stdout, result.stdout


def test_runserver_serves_landing_page(project_venv):
    """The full journey: boot the dev server and fetch the landing page over HTTP.

    This is ``make bootstrap`` -> ``make runserver`` -> open the browser, which
    is how the Python 3.14 breakage was found in the first place.
    """
    # The landing page itself needs no table, but the session/auth middleware a
    # real request passes through does, and migrating is cheap and idempotent.
    run(
        [project_venv.python, "src/manage.py", "migrate", "--noinput"],
        cwd=project_venv.project_dir,
        env=_debug_env(project_venv),
    )

    port = _free_port()
    with _runserver(project_venv, port) as process:
        status, body = _get_until_up(process, "http://127.0.0.1:{0}/".format(port))

    assert status == 200, "GET / returned {0}:\n\n{1}".format(status, body[:4000])
    assert LANDING_HEADLINE in body, body[:4000]
    assert TAILWIND_STYLESHEET in body, body[:4000]
