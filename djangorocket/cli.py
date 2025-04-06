import click
from cookiecutter.main import cookiecutter

from djangorocket.components import add_components

@click.group()
def main():
    pass


@main.command()
def init():
    """Run the cookiecutter template in the root folder."""
    cookiecutter("./templates/projects/base")

@main.command()
@click.argument("components", nargs=-1)
def add(components):
    """Add a UI cookiecutter template to an existing DjangoRocket project."""
    add_components(components)
