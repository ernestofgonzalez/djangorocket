"""Wire a throwaway "playground" project to a local ``djangorocket`` checkout.

Backs ``make playground``: scaffolds a project with ``djangorocket init`` and
then points the CLI at the checkout in two places, because a playground is only
useful if the command you type inside it runs the code you are working on:

* the playground's own virtualenv, so the project's tooling (and an activated
  shell) uses the checkout;
* the ``djangorocket`` on ``PATH``, via a pipx editable install, because a fresh
  terminal has no virtualenv activated -- so a bare ``djangorocket add ...``
  would otherwise run whichever release sits earliest on ``PATH``.

Either half can be run on its own: ``make playground-link PROJECT=<dir>`` for a
playground that already exists, ``make linkcli`` for the command on ``PATH``.

Which checkout gets linked is parametrised -- ``--source-dir``, or
``DJANGOROCKET_SRC_DIR`` in ``.env``, defaulting to the checkout this script
lives in -- so a second working tree can be exercised without touching the
first.

Kept to the standard library plus the checkout's own dependencies: it runs from
the repo's development environment, which already has ``click`` and
``cookiecutter`` (see ``requirements/requirements.txt``).
"""

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# tools/playground.py -> the checkout this script belongs to.
REPO_ROOT = Path(__file__).resolve().parents[1]

# Must match the generated project's Makefile, so the virtualenv this script
# creates is the one `make bootstrap` and `make runserver` go on to use.
VENV_DIRNAME = ".venv"

BIN_DIRNAME = "Scripts" if os.name == "nt" else "bin"

# The console script, which is *not* the distribution name: the package ships as
# `djrocket` and installs a `djangorocket` command.
CLI_NAME = "djangorocket"

# What `python -m djangorocket` needs to import before it can scaffold anything.
INIT_REQUIREMENTS = ("click", "cookiecutter")


class PlaygroundError(Exception):
    """A failure worth reporting as a message rather than a traceback."""


def run(cmd, **kwargs):
    """Run ``cmd`` with its output going straight to the terminal."""
    subprocess.run([str(part) for part in cmd], check=True, **kwargs)


def resolve_source_dir(source_dir):
    """Absolute path of the ``djangorocket`` checkout to link, once validated."""
    resolved = Path(source_dir).expanduser().resolve()
    if not (resolved / "djangorocket" / "cli.py").is_file():
        raise PlaygroundError(
            f"{resolved} is not a djangorocket checkout "
            "(no djangorocket/cli.py). Point --source-dir / "
            "DJANGOROCKET_SRC_DIR at one."
        )
    return resolved


def resolve_project_dir(project_dir):
    """Absolute path of an existing playground project, once validated."""
    resolved = Path(project_dir).expanduser().resolve()
    if not resolved.is_dir():
        raise PlaygroundError(f"{resolved} does not exist.")
    if not (resolved / "Makefile").is_file():
        raise PlaygroundError(
            f"{resolved} does not look like a generated project (no Makefile)."
        )
    return resolved


def zip_templates(source_dir):
    """Rebuild the ``<name>.zip`` sitting next to each template directory.

    ``djangorocket add`` reads those zips rather than the template directories
    (see ``djangorocket/components.py``) and they are build artifacts, kept out
    of git. Refreshing them here is what makes a linked playground pick up
    local edits to a UI template. Run from the checkout being linked: the
    script resolves its templates relative to the working directory.
    """
    print("Zipping templates...", flush=True)
    run([sys.executable, source_dir / "tools" / "zip_templates.py"], cwd=source_dir)


def scaffold(source_dir, base_dir):
    """Run the checkout's ``init`` in ``base_dir``; return the project it made.

    ``init`` prompts for a project name and picks the project's directory name
    itself (kebab-cased, de-duplicated against both sibling directories and
    docker volumes), so the prompt is left interactive and the new directory is
    found by comparing ``base_dir`` before and after.
    """
    missing = [
        name for name in INIT_REQUIREMENTS if importlib.util.find_spec(name) is None
    ]
    if missing:
        raise PlaygroundError(
            "{0} cannot import {1}, which `djangorocket init` needs. Install "
            "the development requirements (`pip install -r requirements.txt`) "
            "or point --python at an interpreter that has them.".format(
                sys.executable, " and ".join(missing)
            )
        )

    base_dir.mkdir(parents=True, exist_ok=True)
    before = _child_dirs(base_dir)

    # Prepend the checkout to the subprocess' import path so `init` renders the
    # templates in *this* source tree even when another djangorocket is
    # installed in the environment running it.
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(source_dir), *filter(None, [env.get("PYTHONPATH")])]
    )
    run([sys.executable, "-m", "djangorocket", "init"], cwd=base_dir, env=env)

    created = _child_dirs(base_dir) - before
    if not created:
        raise PlaygroundError(f"`djangorocket init` created no project in {base_dir}.")
    # One directory per run in practice; newest wins if something else appeared
    # in the meantime.
    newest = max(created, key=lambda name: (base_dir / name).stat().st_mtime)
    return base_dir / newest


def _child_dirs(path):
    """Names of the directories directly inside ``path``."""
    try:
        return {entry.name for entry in os.scandir(path) if entry.is_dir()}
    except FileNotFoundError:
        return set()


def link_venv(project_dir, source_dir, python):
    """Install ``source_dir`` in editable mode into ``project_dir``'s virtualenv.

    Builds the virtualenv the generated project's ``make bootstrap`` expects, so
    the two share one environment: ``bootstrap`` re-runs ``python3 -m venv
    .venv`` over an existing virtualenv without clearing it, leaving this
    editable install in place while it adds the project's own requirements.
    """
    venv_dir = project_dir / VENV_DIRNAME
    print(f"Creating virtualenv in {venv_dir}...", flush=True)
    run([python, "-m", "venv", venv_dir])

    venv_python = venv_dir / BIN_DIRNAME / "python"
    run([venv_python, "-m", "pip", "install", "--quiet", "--upgrade", "pip", "wheel"])

    print(f"Installing {source_dir} in editable mode...", flush=True)
    run([venv_python, "-m", "pip", "install", "--quiet", "--editable", source_dir])
    return venv_dir


def link_cli(source_dir):
    """Make the ``djangorocket`` on ``PATH`` an editable install of ``source_dir``.

    The playground's virtualenv is not activated in a fresh terminal, so this is
    the install that a bare ``djangorocket add ...`` typed inside the playground
    actually runs. pipx keeps it in its own environment (rather than in the
    playground's, or the user's site-packages) and ``--force`` lets it reclaim
    the command from an earlier install -- including a pipx environment still
    named after the package's former name, which is how a long-stale release can
    end up shadowing a linked checkout.
    """
    if shutil.which("pipx") is None:
        print(
            f"! pipx is not installed, so the `{CLI_NAME}` on PATH is left "
            f"alone. Install pipx, or run {VENV_DIRNAME}/{BIN_DIRNAME}/{CLI_NAME} "
            "from the playground.",
            flush=True,
        )
        return
    print(f"Linking the `{CLI_NAME}` command on PATH to {source_dir}...", flush=True)
    run(["pipx", "install", "--editable", "--force", source_dir])


def verify_cli(source_dir, probe_dir):
    """Report which build a bare ``djangorocket`` runs, and warn if it is wrong.

    The check that catches the failure this whole script exists to prevent: a
    playground wired up perfectly while the command on ``PATH`` resolves to some
    other install, which then fails in ways that look like a bug in the
    playground rather than the wrong binary.
    """
    cli = shutil.which(CLI_NAME)
    if cli is None:
        print(
            f"! `{CLI_NAME}` is not on PATH. Run it as "
            f"{VENV_DIRNAME}/{BIN_DIRNAME}/{CLI_NAME} from the playground.",
            flush=True,
        )
        return
    package = _cli_package_path(cli, probe_dir)
    if package is None:
        print(f"! could not work out which build `{CLI_NAME}` ({cli}) runs.")
        return
    if source_dir in package.parents:
        print(f"✓ `{CLI_NAME}` on PATH is {cli}\n  running {source_dir}")
        return
    print(
        f"! `{CLI_NAME}` on PATH ({cli}) runs {package.parent}, "
        f"not {source_dir}.\n"
        f"  Link it with: pipx install --editable --force {source_dir}"
    )


def _cli_package_path(cli_path, probe_dir):
    """Path of the ``djangorocket`` package a console script imports, or None.

    Console scripts hard-code an absolute interpreter in their shebang, so
    asking that interpreter is the one reliable way to tell which build the
    command runs. Probed from ``probe_dir``, which must not be a checkout: the
    working directory comes first on ``sys.path`` and would shadow whatever is
    installed.
    """
    try:
        shebang = Path(cli_path).read_text(errors="replace").splitlines()[0]
    except (OSError, IndexError, ValueError):
        return None
    if not shebang.startswith("#!"):
        return None
    interpreter = shebang[2:].strip().strip('"')
    probe = subprocess.run(
        [interpreter, "-c", f"import {CLI_NAME}; print({CLI_NAME}.__file__)"],
        cwd=str(probe_dir),
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0 or not probe.stdout.strip():
        return None
    return Path(probe.stdout.strip()).resolve()


def report(source_dir, project_dir, venv_dir, linked_cli):
    """Print what was linked and the commands that follow from it."""
    print()
    if project_dir is None:
        print(f"✓ Linked the `{CLI_NAME}` command to {source_dir}")
        return

    print(f"✓ Linked {source_dir} into {project_dir.name}/{venv_dir.name}")
    print("  Boot the playground (installs its requirements, starts services):")
    print(f"    cd {project_dir}")
    print("    make bootstrap")
    # Without the command on PATH linked, a bare `djangorocket` is whatever else
    # is installed, so name the virtualenv's copy explicitly.
    cli = CLI_NAME if linked_cli else f"{venv_dir.name}/{BIN_DIRNAME}/{CLI_NAME}"
    print("  Add a component with the local CLI:")
    print(f"    {cli} add accordion")


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--source-dir",
        default=os.environ.get("DJANGOROCKET_SRC_DIR") or str(REPO_ROOT),
        help=(
            "djangorocket checkout to link into the playground "
            "(default: $DJANGOROCKET_SRC_DIR, or this checkout)."
        ),
    )
    parser.add_argument(
        "--base-dir",
        default=os.environ.get("PLAYGROUND_BASE_DIR"),
        help=(
            "directory to scaffold the playground project in "
            "(default: $PLAYGROUND_BASE_DIR)."
        ),
    )
    parser.add_argument(
        "--project-dir",
        default=None,
        help=(
            "link an existing playground project instead of scaffolding a new "
            "one; --base-dir is then unused."
        ),
    )
    parser.add_argument(
        "--python",
        default=os.environ.get("PLAYGROUND_PYTHON") or "python3",
        help=(
            "interpreter used to build the playground's virtualenv "
            "(default: $PLAYGROUND_PYTHON, or python3)."
        ),
    )
    parser.add_argument(
        "--cli-only",
        action="store_true",
        help=(
            f"only link the `{CLI_NAME}` command on PATH, leaving every "
            "playground project untouched."
        ),
    )
    parser.add_argument(
        "--no-link-cli",
        dest="link_cli",
        action="store_false",
        help=(
            f"leave the `{CLI_NAME}` command on PATH alone; only the "
            "playground's own virtualenv is linked."
        ),
    )
    args = parser.parse_args(argv)
    if args.cli_only and not args.link_cli:
        parser.error("--cli-only and --no-link-cli leave nothing to do")
    return args


def main(argv=None):
    args = parse_args(argv)

    # Resolve every path before doing any work, so an unset setting or a wrong
    # path fails before a template is zipped or a project scaffolded.
    source_dir = resolve_source_dir(args.source_dir)
    project_dir = None
    base_dir = None
    if not args.cli_only:
        if args.project_dir:
            project_dir = resolve_project_dir(args.project_dir)
        elif args.base_dir:
            base_dir = Path(args.base_dir).expanduser().resolve()
        else:
            raise PlaygroundError(
                "No playground directory set. Add PLAYGROUND_BASE_DIR to .env "
                "(see .env.example), or pass --base-dir / --project-dir."
            )

    zip_templates(source_dir)

    venv_dir = None
    if not args.cli_only:
        if project_dir is None:
            project_dir = scaffold(source_dir, base_dir)
        venv_dir = link_venv(project_dir, source_dir, args.python)

    if args.link_cli:
        link_cli(source_dir)
        # Probe from the playground, or anywhere that is not a checkout.
        verify_cli(source_dir, project_dir or tempfile.gettempdir())

    report(source_dir, project_dir, venv_dir, args.link_cli)


if __name__ == "__main__":
    try:
        main()
    except PlaygroundError as error:
        sys.exit(f"Error: {error}")
    except subprocess.CalledProcessError as error:
        sys.exit(
            f"Error: `{' '.join(error.cmd)}` failed with exit code {error.returncode}."
        )
