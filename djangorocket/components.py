import importlib.resources

from cookiecutter.main import cookiecutter

UI_TEMPLATES_PACKAGE = "djangorocket.templates.ui"


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


def add_components(components, templates_dir=None):
    for component_name in components:
        add_component(component_name, templates_dir)


def add_component(component_name, templates_dir=None):
    """Render the ``component_name`` UI template into ``templates_dir``."""
    resource = importlib.resources.files(UI_TEMPLATES_PACKAGE).joinpath(
        f"{component_name}.zip"
    )
    if not resource.is_file():
        raise ValueError(
            f"unknown component '{component_name}'. "
            f"Available components: {', '.join(available_components()) or 'none'}."
        )

    # cookiecutter needs a real filesystem path, which a zipped install does not
    # expose directly; ``as_file`` materialises one for the duration of the block.
    with importlib.resources.as_file(resource) as template_path:
        cookiecutter(str(template_path), output_dir=templates_dir)
