import click
from cookiecutter.main import cookiecutter

from djangorocket.components import add_components
from djangorocket.django import DjangoSettingsManager

@click.group()
def main():
    pass

@main.command()
def init():
    """Run the cookiecutter template in the root folder."""
    cookiecutter("./templates/projects/base")

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
