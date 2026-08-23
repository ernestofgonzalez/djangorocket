"""End-to-end tests for the ``djangorocket add`` command.

The product journey exercised here is: install the CLI -> run
``djangorocket add accordion`` -> a ready-to-use UI template lands in the
project. These tests drive the *real* console-script entry point in a
subprocess and assert the template is written and fully rendered.

They only need cookiecutter and the installed ``djangorocket`` CLI (both present
in the test environment), so - like ``test_scaffold.py`` - they run as part of
the normal ``pytest`` invocation rather than behind ``--run-e2e``.
"""

import importlib.util
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from .conftest import REPO_ROOT

ACCORDION_TEMPLATE = REPO_ROOT / "djangorocket" / "templates" / "ui" / "accordion"
ZIP_TOOL = REPO_ROOT / "tools" / "zip_templates.py"


def _djangorocket_cli():
    """Locate the installed ``djangorocket`` console script."""
    found = shutil.which("djangorocket")
    if found:
        return found
    # Console scripts are installed alongside the interpreter running the tests.
    candidate = Path(sys.executable).parent / "djangorocket"
    return str(candidate) if candidate.exists() else None


def _run_add(*args, cwd):
    """Run ``djangorocket add ...`` via the real console script.

    ``add`` prompts for cookiecutter's ``project_slug`` (it does not pass
    ``no_input``), so feed a newline to accept the default. It also swallows
    errors and always exits 0, so callers must assert on the filesystem and
    output, not on the return code.
    """
    cli = _djangorocket_cli()
    if cli is None:
        pytest.skip("djangorocket console script not found")
    return subprocess.run(
        [cli, "add", *args],
        cwd=str(cwd),
        input="\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


@pytest.fixture(scope="session")
def accordion_zip():
    """Regenerate the packaged ``accordion.zip`` from source via the project tool.

    ``add`` loads this zip through ``importlib.resources``; it is a gitignored
    build artifact that ``setup.py`` rebuilds on install. Regenerating it here
    keeps the test hermetic and also exercises the packaging tool end to end.
    """
    spec = importlib.util.spec_from_file_location("zip_templates", ZIP_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.zip_template(str(ACCORDION_TEMPLATE))

    zip_path = ACCORDION_TEMPLATE.with_suffix(".zip")
    assert zip_path.is_file()
    return zip_path


def test_packaged_zip_starts_with_top_level_dir(accordion_zip):
    """cookiecutter unpacks a zip by treating ``namelist()[0]`` as the project
    root, so the first entry must be the single top-level ``accordion/``
    directory - otherwise the archive is unusable."""
    names = zipfile.ZipFile(accordion_zip).namelist()
    assert names[0] == "accordion/", names


def test_add_accordion_writes_rendered_template(tmp_path, accordion_zip):
    result = _run_add("accordion", "--templates-dir", str(tmp_path), cwd=tmp_path)
    assert "Error:" not in result.stdout, result.stdout

    rendered = tmp_path / "accordion" / "accordion.html"
    assert rendered.is_file(), result.stdout

    text = rendered.read_text(encoding="utf-8")
    assert "<span></span>" in text
    # No cookiecutter/jinja scaffolding should survive into the generated file.
    assert "{{ cookiecutter" not in text
    assert "{% raw %}" not in text and "{% endraw %}" not in text


def test_add_accordion_discovers_templates_dir_from_settings(baked_project, accordion_zip):
    """Run from inside a baked project so the CLI must read ``TEMPLATES['DIRS']``
    from ``settings.py`` (resolving ``BASE_DIR`` relative to the settings file).
    Generated projects put templates at ``src/templates``."""
    result = _run_add("accordion", cwd=baked_project)
    assert "Error:" not in result.stdout, result.stdout

    rendered = baked_project / "src" / "templates" / "accordion" / "accordion.html"
    assert rendered.is_file(), result.stdout
