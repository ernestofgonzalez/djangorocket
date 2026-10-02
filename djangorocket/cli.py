import contextlib
import importlib.resources
import itertools
import os
import re
import socket
import subprocess
import sys
import threading
import time

import click
from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import OutputDirExistsException

from djangorocket.components import add_components
from djangorocket.django import DjangoSettingsManager

@click.group()
def main():
    pass


@contextlib.contextmanager
def _spinner(message):
    """Show an animated 'working' indicator while a slow step runs.

    Generating a project renders well over a hundred files with no output of its
    own, which makes the command look hung. This keeps the terminal alive with a
    spinner on a TTY, and falls back to a single plain line otherwise (e.g. when
    output is piped or running in CI).
    """
    if not sys.stderr.isatty():
        click.echo(message, err=True)
        yield
        return

    done = threading.Event()

    def spin():
        for frame in itertools.cycle("|/-\\"):
            if done.is_set():
                break
            click.echo(f"\r{frame} {message}", nl=False, err=True)
            time.sleep(0.1)
        click.echo("\r\033[K", nl=False, err=True)  # clear the spinner line

    thread = threading.Thread(target=spin)
    thread.start()
    try:
        yield
    finally:
        done.set()
        thread.join()


def _slugify_dirname(project_name):
    """Kebab-case a project name for use as a directory / docker identifier."""
    slug = re.sub(r"[^a-z0-9]+", "-", project_name.lower()).strip("-")
    return slug or "project"


def _existing_docker_volume_names():
    """Names of existing docker volumes, or empty set when docker is unavailable."""
    try:
        result = subprocess.run(
            ["docker", "volume", "ls", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return set()
    return set(result.stdout.split())


def _available_project_dirname(base, output_dir, taken_volumes):
    """First of ``base``, ``base-1``, ``base-2``, ... free on disk and in docker.

    A generated project's docker-compose names its volumes ``<dirname>_postgres_data``
    and ``<dirname>_redis_data``, so we also skip a name whose volumes already exist
    even when the directory does not (e.g. a previous project was removed but its
    data volumes lingered).
    """

    def is_taken(name):
        if os.path.exists(os.path.join(output_dir, name)):
            return True
        return any(
            "{0}_{1}".format(name, suffix) in taken_volumes
            for suffix in ("postgres_data", "redis_data")
        )

    candidate = base
    counter = 0
    while is_taken(candidate):
        counter += 1
        candidate = "{0}-{1}".format(base, counter)
    return candidate


def _port_is_free(port):
    """True if ``port`` can be bound on this host right now."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("", port))
            return True
        except OSError:
            return False


def _reserved_sibling_ports(output_dir):
    """Host ports already assigned to sibling projects' ``.env`` files.

    ``init`` picks ports that are free *now*, but a project created a moment ago
    may not have its containers up yet, so its port would still look free. Reading
    the ports it reserved in ``.env`` lets us hand out distinct ones to each
    project generated in the same directory.
    """
    reserved = set()
    try:
        entries = os.listdir(output_dir)
    except OSError:
        return reserved
    for entry in entries:
        env_path = os.path.join(output_dir, entry, ".env")
        if not os.path.isfile(env_path):
            continue
        try:
            with open(env_path) as env_file:
                for line in env_file:
                    match = re.match(r"(?:POSTGRES_PORT|REDIS_PORT)=(\d+)\s*$", line)
                    if match:
                        reserved.add(int(match.group(1)))
        except OSError:
            continue
    return reserved


def _pick_host_port(preferred, reserved):
    """First port from ``preferred`` up that is free and not already reserved.

    Mutates ``reserved`` so the same call site can pick several distinct ports
    (e.g. Postgres then Redis) without handing out a duplicate.
    """
    port = preferred
    while port in reserved or not _port_is_free(port):
        port += 1
    reserved.add(port)
    return port


@main.command()
def init():
    """Scaffold a new DjangoRocket project in the current directory."""
    project_name = click.prompt("Project name", default="My Project")
    base_template = importlib.resources.files("djangorocket.templates.projects").joinpath("base")

    output_dir = os.getcwd()

    # Pick a project directory name that is free both on disk and as a docker
    # volume prefix, so several generated projects can coexist on one machine.
    project_dirname = _available_project_dirname(
        _slugify_dirname(project_name),
        output_dir,
        _existing_docker_volume_names(),
    )

    # Pick free host ports so several projects' Postgres/Redis can run at once.
    reserved_ports = _reserved_sibling_ports(output_dir)
    postgres_host_port = _pick_host_port(5432, reserved_ports)
    redis_host_port = _pick_host_port(6379, reserved_ports)

    try:
        with _spinner("Creating your project..."):
            project_dir = cookiecutter(
                str(base_template),
                no_input=True,
                extra_context={
                    "project_name": project_name,
                    "project_dirname": project_dirname,
                    "postgres_host_port": str(postgres_host_port),
                    "redis_host_port": str(redis_host_port),
                },
            )
    except OutputDirExistsException as e:
        detail = str(e).removeprefix("Error: ")
        raise click.ClickException(
            f"{detail}. Remove it or pick a different project name and try again."
        )

    click.echo(click.style(f"✓ Created {os.path.relpath(project_dir)}", fg="green"))
    # Point at the absolute path: `init` may have been run from anywhere (e.g.
    # `make playground` runs it in $PLAYGROUND_BASE_DIR), and the next step is
    # opening the project in an editor, not cd-ing in this shell.
    click.echo(f"  Open the project in your editor: {os.path.abspath(project_dir)}")


@main.command()
@click.argument("components", nargs=-1)
@click.option("--templates-dir", default=None, help="Directory where the new template source file should be added to.")
def add(components, templates_dir):
    """Add a UI cookiecutter template to an existing DjangoRocket project."""
    try:
        if templates_dir is None:
            django_settings = DjangoSettingsManager()
            templates_dir = django_settings.get_templates_dir()

        add_components(components, templates_dir)
    except Exception as e:
        click.echo(f"Error: {e}")
