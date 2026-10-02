"""Fast structural checks on a freshly baked project.

These only need cookiecutter (a core dependency), so they run as part of the
normal ``pytest`` invocation and give quick feedback that the template renders.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

from .conftest import bake

# Files that every generated project must contain, relative to the project root.
# The dotfiles are listed deliberately: they are easy to lose from a built
# package (a MANIFEST.in tweak, a different build backend) without anything else
# in the scaffold changing.
EXPECTED_FILES = [
    "src/manage.py",
    "src/my_project/settings.py",
    "src/my_project/urls.py",
    "src/my_project/wsgi.py",
    "src/my_project/asgi.py",
    "requirements/requirements.txt",
    "requirements/requirements-testing.txt",
    # The compiled Tailwind stylesheet `{% tailwind_css %}` resolves to. It ships
    # prebuilt so onboarding needs no Node; without it a project renders unstyled
    # and raises on the staticfiles manifest lookup once DEBUG is off.
    "src/tailwind_theme/static/css/dist/styles.css",
    "Makefile",
    "README.md",
    "pytest.ini",
    "pyproject.toml",
    "docker-compose.yml",
    ".coveragerc",
    ".env.example",
    ".flake8",
    ".gitignore",
    ".isort.cfg",
]

# Local artifacts a generated project produces -- the virtualenv `make bootstrap`
# creates, the coverage output `make coverage` writes, and the `.env` the post-gen
# hook seeds with a real SECRET_KEY -- none of which may reach a commit.
GITIGNORED_PATHS = [
    ".env",
    ".venv/",
    "__pycache__/",
    "db.sqlite3",
    "src/staticfiles/",
    "src/tailwind_theme/static_src/node_modules/",
    ".coverage",
    "coverage.xml",
    "coverage.svg",
    "htmlcov/",
    ".DS_Store",
]

# The mirror image: paths the scaffold ships, or that a project would plausibly
# add, which the `.gitignore` must NOT swallow. The compiled Tailwind stylesheet
# is the cautionary case -- a bare `dist` pattern inherited from JS boilerplate
# once hid it, so `git init && git add .` yielded a project with no CSS. The
# module names below are the other half of that problem: generic Python-packaging
# boilerplate (`lib/`, `var/`, `build/`, `target/` ...) shadows ordinary app
# directories in a project that never builds an sdist.
GITIGNORE_TRACKED_PATHS = [
    "src/tailwind_theme/static/css/dist/styles.css",
    "src/tailwind_theme/static_src/package-lock.json",
    "src/static/CACHE/manifest.json",
    ".env.example",
    "README.md",
    "lib/models.py",
    "var/models.py",
    "build/models.py",
    "dist/models.py",
    "out/models.py",
    "target/models.py",
    "coverage/models.py",
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
    # "My Project" -> kebab directory "my-project"; the Python package inside
    # stays snake_case (src/my_project).
    assert baked_project.name == "my-project"


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
    """A custom project name drives both the kebab dir and the snake package."""
    project = bake(tmp_path, extra_context={"project_name": "Cool SaaS App"})
    assert project.name == "cool-saas-app"
    assert (project / "src/cool_saas_app/settings.py").is_file()


@pytest.fixture
def git_project(tmp_path):
    """A freshly baked project with a git repo initialised in its root.

    Its own bake rather than the session fixture's, because this inits a repo in
    the project root and nothing else should inherit that.
    """
    if shutil.which("git") is None:
        pytest.skip("needs git to check the generated .gitignore")
    project = bake(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    return project


def _is_ignored(project, path):
    """Whether git would ignore ``path`` inside ``project``."""
    result = subprocess.run(["git", "check-ignore", "-q", path], cwd=project)
    return result.returncode == 0


def test_gitignore_covers_local_artifacts(git_project):
    """The shipped ``.gitignore`` keeps generated secrets and build output out of git.

    Asserted through ``git check-ignore`` rather than by grepping the file, so
    what is pinned is the behaviour a user gets after ``git init``, not the exact
    wording of the patterns.
    """
    missed = [path for path in GITIGNORED_PATHS if not _is_ignored(git_project, path)]
    assert not missed, f"not ignored by the generated .gitignore: {missed}"


def test_gitignore_does_not_hide_project_files(git_project):
    """...and does not hide the project's own source along the way."""
    swallowed = [
        path for path in GITIGNORE_TRACKED_PATHS if _is_ignored(git_project, path)
    ]
    assert not swallowed, f"wrongly ignored by the generated .gitignore: {swallowed}"
