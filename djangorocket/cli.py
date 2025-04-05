import click
from cookiecutter.main import cookiecutter


@click.group()
def main():
    pass


@main.command()
def init():
    """Run the cookiecutter template in the root folder."""
    cookiecutter("./templates/projects/base")
