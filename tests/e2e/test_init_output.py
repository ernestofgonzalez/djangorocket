"""What ``djangorocket init`` tells the user once the project exists.

``init`` renders the project into the *current* directory, which is rarely the
directory the user is sitting in: ``make playground`` runs it inside
``$PLAYGROUND_BASE_DIR``, and the command is often invoked from a wrapper. A
relative ``cd <project>`` hint was therefore useless -- it only worked in the
shell ``init`` happened to run in. The closing line instead points at the
absolute location so the user can open the project wherever it landed.

Like ``test_init_collision.py`` these exercise the real command, here in-process
through click's ``CliRunner``, and run in the normal ``pytest`` invocation. The
expected directory name is read back from ``tmp_path`` rather than hardcoded,
because ``init`` legitimately suffixes it (``-1``, ``-2``, ...) when the name is
already taken on this machine.
"""

import os
from collections import namedtuple

import pytest
from click.testing import CliRunner

from djangorocket.cli import main

PROJECT_NAME = "Men I Trust Web Blog"

InitRun = namedtuple("InitRun", ["output", "project_dir"])


@pytest.fixture
def init_run(tmp_path, monkeypatch):
    """Run ``init`` in ``tmp_path``, answering the project-name prompt."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(main, ["init"], input=PROJECT_NAME + "\n")
    assert result.exit_code == 0, result.output

    created = [path for path in tmp_path.iterdir() if path.is_dir()]
    assert len(created) == 1, created
    return InitRun(output=result.output, project_dir=created[0])


def _closing_line(output):
    """The last non-empty line of ``init``'s output."""
    return [line.strip() for line in output.splitlines() if line.strip()][-1]


def test_init_reports_the_created_project(init_run):
    """The project is named relative to where the user ran the command."""
    assert "✓ Created {0}".format(init_run.project_dir.name) in init_run.output


def test_init_prompts_to_open_the_project_at_its_absolute_path(init_run):
    """The closing line invites the user to open the project where it landed."""
    line = _closing_line(init_run.output)
    assert "Open the project" in line

    printed = line.split(": ", 1)[1]
    assert os.path.isabs(printed), printed
    # Resolve both sides: tmp_path may be reached through a symlinked /tmp.
    assert os.path.realpath(printed) == os.path.realpath(str(init_run.project_dir))
    assert os.path.isdir(printed)


def test_init_does_not_print_a_cd_hint(init_run):
    """The old ``cd <project>`` line is gone: it was dead advice (see module docs)."""
    assert "cd {0}".format(init_run.project_dir.name) not in init_run.output
