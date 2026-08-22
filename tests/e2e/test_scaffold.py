"""Fast structural checks on a freshly baked project.

These only need cookiecutter (a core dependency), so they run as part of the
normal ``pytest`` invocation and give quick feedback that the template renders.
"""

from pathlib import Path

import pytest

from .conftest import bake

# Files that every generated project must contain, relative to the project root.
EXPECTED_FILES = [
    "src/manage.py",
    "src/my_project/settings.py",
    "src/my_project/urls.py",
    "src/my_project/wsgi.py",
    "src/my_project/asgi.py",
    "requirements/requirements.txt",
    "requirements/requirements-testing.txt",
    "Makefile",
    "README.md",
    "pytest.ini",
    "pyproject.toml",
    "docker-compose.yml",
    ".env.example",
]


def _iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary asset (fonts, images) - nothing to template-check


def test_bake_succeeds(baked_project):
    assert baked_project.is_dir()
    # Default cookiecutter.json project_name "My Project" -> slug "my_project".
    assert baked_project.name == "my_project"


@pytest.mark.parametrize("relative_path", EXPECTED_FILES)
def test_expected_files_present(baked_project, relative_path):
    assert (baked_project / relative_path).is_file(), f"missing {relative_path}"


def test_no_unrendered_cookiecutter_tokens(baked_project):
    """No '{{ cookiecutter.* }}' placeholders should survive in files or paths."""
    offenders = []
    for path, text in _iter_text_files(baked_project):
        if "{{" in text and "cookiecutter" in text:
            offenders.append(str(path.relative_to(baked_project)))
    assert not offenders, f"unrendered tokens in: {offenders}"

    path_offenders = [
        str(p.relative_to(baked_project))
        for p in baked_project.rglob("*")
        if "cookiecutter" in p.name
    ]
    assert not path_offenders, f"unrendered tokens in paths: {path_offenders}"


def test_settings_reference_rendered_slug(baked_project):
    settings = (baked_project / "src/my_project/settings.py").read_text(encoding="utf-8")
    assert '"my_project.auth"' in settings
    assert '"my_project.billing"' in settings
    assert "{{ cookiecutter" not in settings


def test_project_name_drives_slug(tmp_path):
    """A custom project name is slugified into the package/directory name."""
    project = bake(tmp_path, extra_context={"project_name": "Cool SaaS App"})
    assert project.name == "cool_saas_app"
    assert (project / "src/cool_saas_app/settings.py").is_file()
