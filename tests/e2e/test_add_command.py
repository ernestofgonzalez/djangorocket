"""End-to-end tests for the ``djangorocket add`` command.

The product journey exercised here is: install the CLI -> run
``djangorocket add <component>`` -> a ready-to-use UI template lands in the
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

UI_TEMPLATES = REPO_ROOT / "djangorocket" / "templates" / "ui"
ZIP_TOOL = REPO_ROOT / "tools" / "zip_templates.py"

# Where `add` writes a component inside a project's templates directory;
# mirrors COMPONENTS_SUBDIR in djangorocket/components.py.
COMPONENTS_SUBDIR = Path("components") / "ui"


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

    Stdin is empty on purpose: ``add`` must not ask anything, so any prompt it
    grows back hits EOF and fails the calling test instead of passing on a
    default that was never typed. Stderr is folded into stdout because a failure
    is reported there (``click`` writes a ``ClickException`` to stderr), and
    tests assert on the message as well as the exit code.
    """
    cli = _djangorocket_cli()
    if cli is None:
        pytest.skip("djangorocket console script not found")
    return subprocess.run(
        [cli, "add", *args],
        cwd=str(cwd),
        input="",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


@pytest.fixture(scope="session")
def ui_zips():
    """Regenerate every packaged UI template zip from source via the project tool.

    ``add`` loads these zips through ``importlib.resources``; they are gitignored
    build artifacts that ``setup.py`` rebuilds on install. Regenerating them here
    keeps the tests hermetic and also exercises the packaging tool end to end.
    Every template is zipped, not just the one under test, so ``add``'s component
    lookup sees the same set a real install ships.
    """
    spec = importlib.util.spec_from_file_location("zip_templates", ZIP_TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    zips = {}
    for template in sorted(p for p in UI_TEMPLATES.iterdir() if p.is_dir()):
        if not (template / "cookiecutter.json").is_file():
            continue
        module.zip_template(str(template))
        zip_path = template.with_suffix(".zip")
        assert zip_path.is_file()
        zips[template.name] = zip_path

    # Both shipped components must be there, or a passing suite means nothing.
    assert {"accordion", "button"} <= set(zips), sorted(zips)
    return zips


@pytest.mark.parametrize("component", ["accordion", "button"])
def test_packaged_zip_starts_with_top_level_dir(ui_zips, component):
    """cookiecutter unpacks a zip by treating ``namelist()[0]`` as the project
    root, so the first entry must be the single top-level ``<component>/``
    directory - otherwise the archive is unusable."""
    names = zipfile.ZipFile(ui_zips[component]).namelist()
    assert names[0] == f"{component}/", names


@pytest.mark.parametrize("components", [("accordion",), ("accordion", "button")])
def test_add_never_prompts(tmp_path, ui_zips, components):
    """``add`` renders without asking the caller anything.

    A component's ``cookiecutter.json`` pins ``project_slug`` to the component
    name -- the name already given on the command line -- so there is nothing to
    decide. ``add`` used to call cookiecutter without ``no_input`` anyway and
    stopped on a ``project_slug [button]:`` prompt, once per component named,
    whose only sensible answer was the default. ``_run_add`` passes empty stdin,
    so a prompt that comes back reads EOF and fails here instead of silently
    accepting a default nobody typed.
    """
    result = _run_add(*components, "--templates-dir", str(tmp_path), cwd=tmp_path)

    assert result.returncode == 0, result.stdout
    assert "project_slug" not in result.stdout, result.stdout
    assert "Error:" not in result.stdout, result.stdout
    for component in components:
        rendered = tmp_path / COMPONENTS_SUBDIR / component / f"{component}.html"
        assert rendered.is_file(), result.stdout


def test_add_accordion_writes_rendered_template(tmp_path, ui_zips):
    result = _run_add("accordion", "--templates-dir", str(tmp_path), cwd=tmp_path)
    assert "Error:" not in result.stdout, result.stdout

    rendered = tmp_path / COMPONENTS_SUBDIR / "accordion" / "accordion.html"
    assert rendered.is_file(), result.stdout

    text = rendered.read_text(encoding="utf-8")
    # The component ships as a Django include: its own markup, styles and script.
    assert "dr-accordion" in text
    assert "{% for item in items %}" in text
    assert 'role="region"' in text
    # No cookiecutter/jinja scaffolding should survive into the generated file.
    assert "{{ cookiecutter" not in text
    assert "{% raw %}" not in text and "{% endraw %}" not in text


def test_add_accordion_discovers_templates_dir_from_settings(baked_project, ui_zips):
    """Run from inside a baked project so the CLI must read ``TEMPLATES['DIRS']``
    from ``settings.py`` (resolving ``BASE_DIR`` relative to the settings file).
    Generated projects put templates at ``src/templates``."""
    result = _run_add("accordion", cwd=baked_project)
    assert "Error:" not in result.stdout, result.stdout

    rendered = (
        baked_project / "src" / "templates" / COMPONENTS_SUBDIR / "accordion"
    ) / "accordion.html"
    assert rendered.is_file(), result.stdout


def test_add_button_writes_rendered_template(tmp_path, ui_zips):
    result = _run_add("button", "--templates-dir", str(tmp_path), cwd=tmp_path)
    assert "Error:" not in result.stdout, result.stdout

    rendered = tmp_path / COMPONENTS_SUBDIR / "button" / "button.html"
    assert rendered.is_file(), result.stdout

    text = rendered.read_text(encoding="utf-8")
    # The component ships as a Django include: its own markup, styles and script.
    assert "dr-btn" in text
    assert 'btn_tag=href|yesno:"a,button"' in text
    # The icon sprite the asset block carries, and the loading contract.
    assert 'id="dr-btn-i-plus"' in text
    assert 'aria-busy="true"' in text
    # No cookiecutter/jinja scaffolding should survive into the generated file.
    assert "{{ cookiecutter" not in text
    assert "{% raw %}" not in text and "{% endraw %}" not in text


def test_add_writes_into_components_ui_of_the_templates_dir(baked_project, ui_zips):
    """A component lands at ``<templates>/components/ui/<name>/``.

    Run inside a baked project so the destination is the one the CLI discovers
    from ``settings.py`` -- the templates root, ``src/templates`` -- rather than
    one a test handed it. ``add`` used to render straight into that root, which
    mixed the UI kit in with the project's own templates and gave components an
    include path (``accordion/accordion.html``) that read like a project
    template.
    """
    result = _run_add("button", cwd=baked_project)
    templates_dir = baked_project / "src" / "templates"

    rendered = templates_dir / COMPONENTS_SUBDIR / "button" / "button.html"
    assert rendered.is_file(), result.stdout
    # Not at the templates root, where it used to go.
    assert not (templates_dir / "button").exists(), result.stdout
    # The project's own templates, components/ included, are left alone.
    assert (templates_dir / "components" / "header.html").is_file()
    assert (templates_dir / "base.html").is_file()

    # The usage example the component carries must name the path it is actually
    # includable at, or the first thing a user copies out of it is broken.
    text = rendered.read_text(encoding="utf-8")
    assert '{% include "components/ui/button/button.html"' in text


def test_rendered_component_includes_at_its_documented_path(tmp_path, ui_zips):
    """The path a component documents is the path Django resolves.

    Placement and documentation have to move together: a component written to
    ``components/ui/`` whose own usage example still said
    ``{% include "button/button.html" %}`` would break on the first line a user
    copies out of it. Rendered through Django's template engine with the
    templates directory as the only ``DIRS`` entry, which is how a generated
    project configures ``TEMPLATES``.
    """
    pytest.importorskip("django")
    from django.template import Context, Engine

    _run_add("button", "--templates-dir", str(tmp_path), cwd=tmp_path)

    engine = Engine(dirs=[str(tmp_path)])
    rendered = engine.from_string(
        '{% include "components/ui/button/button.html" with label="Create project" %}'
    ).render(Context({}))

    assert "Create project" in rendered
    assert "dr-btn" in rendered


def test_add_reports_where_each_component_landed(tmp_path, ui_zips):
    """``add`` names the directory it wrote, per component.

    It renders without prompting and Django's include path is not obvious from
    the command, so the path is the one thing worth printing.
    """
    result = _run_add(
        "accordion", "button", "--templates-dir", str(tmp_path), cwd=tmp_path
    )

    assert result.returncode == 0, result.stdout
    for component in ("accordion", "button"):
        assert str(COMPONENTS_SUBDIR / component) in result.stdout, result.stdout


def test_add_templates_dir_option_sets_the_templates_root(tmp_path, ui_zips):
    """``--templates-dir`` points at the templates root, wherever it is.

    The layout inside it does not change: the component still lands under
    ``components/ui/``, so a caller passing the option and a project relying on
    ``settings.py`` discovery get the same include path. Missing directories are
    created, so the option works against an empty tree.
    """
    templates_dir = tmp_path / "somewhere" / "else" / "templates"

    result = _run_add("button", "--templates-dir", str(templates_dir), cwd=tmp_path)

    assert result.returncode == 0, result.stdout
    assert (
        templates_dir / COMPONENTS_SUBDIR / "button" / "button.html"
    ).is_file(), result.stdout
    # Nothing was written next to the requested root.
    assert not (tmp_path / "button").exists(), result.stdout


def test_add_templates_dir_option_rejects_a_file(tmp_path, ui_zips):
    """A file path is refused up front, rather than failing mid-render."""
    not_a_dir = tmp_path / "settings.py"
    not_a_dir.write_text("", encoding="utf-8")

    result = _run_add("button", "--templates-dir", str(not_a_dir), cwd=tmp_path)

    assert result.returncode != 0, result.stdout
    assert not (tmp_path / COMPONENTS_SUBDIR).exists(), result.stdout


def test_add_unknown_component_reports_error(tmp_path, ui_zips):
    """An unrecognised name must be refused, not silently resolved to another
    template. ``add`` used to hardcode ``accordion.zip``, so ``add navbar``
    cheerfully installed an accordion."""
    result = _run_add("navbar", "--templates-dir", str(tmp_path), cwd=tmp_path)

    # Non-zero, so a script or a CI step notices: `add` used to echo the error
    # and still exit 0, which made every failure look like a successful no-op.
    assert result.returncode != 0, result.stdout
    assert "unknown component 'navbar'" in result.stdout, result.stdout
    # The error names what the install actually offers, so the user can recover.
    assert "accordion" in result.stdout, result.stdout
    assert "button" in result.stdout, result.stdout
    # Nothing was written: no stray template, and not even the
    # components/ui/ directory `add` would have rendered into.
    assert not (tmp_path / "accordion").exists(), result.stdout
    assert not (tmp_path / COMPONENTS_SUBDIR).exists(), result.stdout
    assert list(tmp_path.iterdir()) == [], list(tmp_path.iterdir())


def test_add_renders_each_requested_component(tmp_path, ui_zips):
    """Every name in the argument list is resolved on its own.

    The old loop ignored ``component_name``, so the number of rendered templates
    was driven by the argument *count* rather than the arguments themselves.
    """
    result = _run_add(
        "accordion", "button", "--templates-dir", str(tmp_path), cwd=tmp_path
    )

    assert "Error:" not in result.stdout, result.stdout
    assert (
        tmp_path / COMPONENTS_SUBDIR / "accordion" / "accordion.html"
    ).is_file(), result.stdout
    assert (
        tmp_path / COMPONENTS_SUBDIR / "button" / "button.html"
    ).is_file(), result.stdout


def test_add_stops_at_an_unknown_component(tmp_path, ui_zips):
    """A bad name aborts the run, but whatever was resolved before it stays."""
    result = _run_add(
        "accordion", "nope", "--templates-dir", str(tmp_path), cwd=tmp_path
    )

    # The first component rendered before the unknown one aborted the run.
    assert (
        tmp_path / COMPONENTS_SUBDIR / "accordion" / "accordion.html"
    ).is_file(), result.stdout
    assert "unknown component 'nope'" in result.stdout, result.stdout
    assert result.returncode != 0, result.stdout
