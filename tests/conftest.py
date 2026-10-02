"""Global pytest configuration.

The end-to-end tests (marked ``e2e``) bake the cookiecutter template into a real
project, build a dedicated virtualenv and install the generated project's
dependencies. That is slow (minutes) and needs a compiler + libpq for
``psycopg2``, so it is opt-in: pass ``--run-e2e`` (or run ``make test-e2e``).
Without the flag those tests are skipped, keeping the default ``pytest`` run fast.
"""


def pytest_addoption(parser):
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="Run the slow end-to-end tests that bake and boot a generated project.",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-e2e"):
        return

    import pytest

    skip_e2e = pytest.mark.skip(reason="need --run-e2e to run (slow; builds a venv)")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)
