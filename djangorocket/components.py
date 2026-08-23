import importlib

from cookiecutter.main import cookiecutter


def add_components(components, templates_dir=None):
    for component_name in components:
        # Locate the zipped template in the installed package
        dr_template_filepath = "templates/ui/accordion.zip"

        with importlib.resources.path("djangorocket.templates.ui", "accordion.zip") as dr_template_fspath:
            cookiecutter(str(dr_template_fspath), output_dir=templates_dir)