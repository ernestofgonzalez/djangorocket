import contextlib
import importlib.resources
import itertools
import os
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


@main.command()
def init():
    """Scaffold a new DjangoRocket project in the current directory."""
    project_name = click.prompt("Project name", default="My Project")
    base_template = importlib.resources.files("djangorocket.templates.projects").joinpath("base")

    try:
        with _spinner("Creating your project..."):
            project_dir = cookiecutter(
                str(base_template),
                no_input=True,
                extra_context={"project_name": project_name},
            )
    except OutputDirExistsException as e:
        detail = str(e).removeprefix("Error: ")
        raise click.ClickException(
            f"{detail}. Remove it or pick a different project name and try again."
        )

    click.echo(click.style(f"✓ Created {os.path.relpath(project_dir)}", fg="green"))
    click.echo(f"  cd {os.path.relpath(project_dir)}")

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
