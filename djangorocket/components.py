import importlib.resources
import os

from cookiecutter.main import cookiecutter

UI_TEMPLATES_PACKAGE = "djangorocket.templates.ui"

# Where a component is written inside the project's templates directory. The UI
# kit keeps its own subdirectory so it stays separate from the templates a
# project owns (a generated project already ships ``templates/components/`` for
# those), and so every component has one predictable include path:
# ``{% include "components/ui/button/button.html" %}``.
COMPONENTS_SUBDIR = ("components", "ui")


def available_components():
    """Names of the UI templates packaged with this install.

    Templates ship as ``<name>.zip`` built from ``templates/ui/<name>/`` by
    ``setup.py`` (see ``tools/zip_templates.py``), so the packaged zips are the
    source of truth for what ``add`` can install.
    """
    return sorted(
        resource.name.removesuffix(".zip")
        for resource in importlib.resources.files(UI_TEMPLATES_PACKAGE).iterdir()
        if resource.name.endswith(".zip")
    )


def components_dir(templates_dir):
    """Directory inside ``templates_dir`` that components are rendered into."""
    return os.path.join(templates_dir, *COMPONENTS_SUBDIR)


def add_components(components, templates_dir):
    """Render each named component; return where each one landed, in order."""
    return [add_component(name, templates_dir) for name in components]


def add_component(component_name, templates_dir):
    """Render ``component_name`` under ``templates_dir``; return its directory."""
    resource = importlib.resources.files(UI_TEMPLATES_PACKAGE).joinpath(
        f"{component_name}.zip"
    )
    if not resource.is_file():
        raise ValueError(
            f"unknown component '{component_name}'. "
            f"Available components: {', '.join(available_components()) or 'none'}."
        )

    # Created only once the name is known to be good, so an unrecognised
    # component leaves the templates directory untouched. Parents included: the
    # project may have no ``components/`` directory at all.
    destination = components_dir(templates_dir)
    os.makedirs(destination, exist_ok=True)

    # cookiecutter needs a real filesystem path, which a zipped install does not
    # expose directly; ``as_file`` materialises one for the duration of the block.
    #
    # ``no_input`` because a component has nothing to ask about: its
    # ``cookiecutter.json`` pins ``project_slug`` to the component name, which is
    # the name the caller already chose on the command line. Without it,
    # ``add button`` stopped on a ``project_slug [button]:`` prompt -- once per
    # component named -- whose only sensible answer was the default.
    with importlib.resources.as_file(resource) as template_path:
        return cookiecutter(str(template_path), output_dir=destination, no_input=True)
