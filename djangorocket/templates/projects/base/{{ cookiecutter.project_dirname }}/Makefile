#!/usr/bin/env bash

LIGHT_CYAN=\033[1;36m
NO_COLOR=\033[0m

# Use the virtualenv created by `make bootstrap` when it exists, so `make test`,
# `make runserver`, etc. work without activating it first. Fall back to the
# system `python3` otherwise (e.g. in CI, where the interpreter is already on
# PATH). Absolute so it keeps working after the `cd src` some targets do.
VENV := .venv
PYTHON := $(shell [ -x $(VENV)/bin/python ] && echo $(CURDIR)/$(VENV)/bin/python || echo python3)

.PHONY: help bootstrap setupdb setupredis runserver test pytest coverage lint format linttemplates formattemplates

help:
	@echo "bootstrap - create a virtualenv, install deps, start services and migrate"
	@echo "setupdb - start the Postgres service with docker compose"
	@echo "setupredis - start the Redis service with docker compose"
	@echo "runserver - run the Django development server"
	@echo "test - run tests quickly with the default Python"
	@echo "pytest - run tests with pytest"
	@echo "coverage - get code coverage report"
	@echo "lint - lint the python code"
	@echo "format - format the python code"
	@echo "linttemplates - lint the Django HTML code"
	@echo "formattemplates - format the Django HTML code"

# One-shot onboarding: everything needed to boot the project from a fresh clone.
# After this finishes, `make runserver` just works.
bootstrap:
	@echo "${LIGHT_CYAN}Creating virtualenv in $(VENV)...${NO_COLOR}"
	python3 -m venv $(VENV)
	@echo "${LIGHT_CYAN}Installing dependencies...${NO_COLOR}"
	$(VENV)/bin/python -m pip install --upgrade pip wheel
	$(VENV)/bin/python -m pip install -r requirements.txt
	$(MAKE) setupdb setupredis
	@echo "${LIGHT_CYAN}Applying migrations...${NO_COLOR}"
	cd src && $(CURDIR)/$(VENV)/bin/python manage.py migrate
	@echo "${LIGHT_CYAN}Done. Start the server with: make runserver${NO_COLOR}"

# Start the Postgres service in the background, waiting until it is healthy.
# On failure `--wait` only prints "container is unhealthy", so dump the service's
# own logs before bailing out: that is where the real error is.
setupdb:
	@echo "${LIGHT_CYAN}Starting Postgres...${NO_COLOR}"
	docker compose up -d --wait postgres || { docker compose logs postgres; exit 1; }

# Start the Redis service in the background, waiting until it is healthy.
setupredis:
	@echo "${LIGHT_CYAN}Starting Redis...${NO_COLOR}"
	docker compose up -d --wait redis || { docker compose logs redis; exit 1; }

# Run the Django development server.
runserver:
	@echo "${LIGHT_CYAN}Starting the development server...${NO_COLOR}"
	cd src && $(PYTHON) manage.py runserver

# Run Django tests
# Run from src/ so Django's test runner discovers the apps: manage.py puts src/
# on sys.path, so tests import as `<project>.<app>...`; starting discovery from
# the repo root (where src/ is not a package) finds nothing. --parallel is left
# off because it requires `tblib` to report failing tests (otherwise it dies
# trying to pickle their tracebacks).
test:
	@echo "${LIGHT_CYAN}Running tests...${NO_COLOR}"
	cd src && $(PYTHON) manage.py test

# Run tests with pytest
pytest:
	@echo "${LIGHT_CYAN}Running tests with pytest...${NO_COLOR}"
	$(PYTHON) -m pytest --durations=1 -n 8

# Get code coverage report
coverage:
	@echo "${LIGHT_CYAN}Running tests and collecting coverage data...${NO_COLOR}"
	$(PYTHON) -m pytest --cov=. -n 8
	$(PYTHON) -m coverage combine
	@echo "${LIGHT_CYAN}Reporting code coverage data...${NO_COLOR}"
	$(PYTHON) -m coverage report
	@echo "${LIGHT_CYAN}Creating HTML report...${NO_COLOR}"
	$(PYTHON) -m coverage html
	@echo "${LIGHT_CYAN}Creating coverage badge...${NO_COLOR}"
	$(PYTHON) -m coverage xml
	genbadge coverage -i coverage.xml -o coverage.svg

# Lint python code
lint:
	@echo "${LIGHT_CYAN}Linting code...${NO_COLOR}"
	isort . --check-only
	black . --check
	flake8 .

# Format python code
format:
	@echo "${LIGHT_CYAN}Formatting code...${NO_COLOR}"
	isort .
	black .

# Lint templates code
linttemplates:
	@echo "${LIGHT_CYAN}Linting Django HTML code...${NO_COLOR}"
	djlint src/ --extension=html --lint

# Format templates code
formattemplates:
	@echo "${LIGHT_CYAN}Linting Django HTML code...${NO_COLOR}"
	djlint src/ --extension=html --reformat
