#!/usr/bin/env bash

LIGHT_CYAN=\033[1;36m
NO_COLOR=\033[0m

# Load developer-local settings (e.g. PLAYGROUND_BASE_DIR) from .env if present.
ifneq (,$(wildcard ./.env))
include .env
export
endif

.PHONY: docs test test-e2e playground playground-link linkcli ziptemplates linttemplates formattemplates

# The Django templates shipped by the base project template. Quoted everywhere
# it is used: the directory name contains both spaces and braces.
TEMPLATES_DIR := djangorocket/templates/projects/base/{{ cookiecutter.project_dirname }}/src

# The checkout a playground's CLI is linked against. Defaults to this repo; set
# it in .env, or on the command line (`make playground
# DJANGOROCKET_SRC_DIR=...`), to develop against a different working tree.
DJANGOROCKET_SRC_DIR ?= $(CURDIR)

# Interpreter that runs this repo's own tooling. `python3` picks up an activated
# development environment, which is where the scripts below find cookiecutter.
PYTHON ?= python3

# Interpreter used to build a playground project's virtualenv, mirroring the
# bare `python3 -m venv` of the generated project's `make bootstrap`. Separate
# from PYTHON so a playground can be built on another Python version.
PLAYGROUND_PYTHON ?= $(PYTHON)

# The playground targets also point the `djangorocket` on PATH at
# $(DJANGOROCKET_SRC_DIR) (a pipx editable install), so the bare command typed
# inside a playground runs the local build without activating anything. Set
# PLAYGROUND_LINK_CLI=0 to link only the playground's own virtualenv.
PLAYGROUND_LINK_CLI ?= 1
LINK_CLI_FLAG := $(if $(filter 0 no false,$(PLAYGROUND_LINK_CLI)),--no-link-cli,)

help:
	@echo "test - run tests (fast; e2e tests are skipped)"
	@echo "test-e2e - run the end-to-end tests (slow; bakes and boots a generated project)"
	@echo "lint - lint the python code"
	@echo "format - format the python code"
	@echo "linttemplates - lint the Django HTML code"
	@echo "formattemplates - format the Django HTML code"
	@echo "ziptemplates - rebuild the template zips \`djangorocket add\` renders"
	@echo "playground - scaffold a throwaway project in \$$PLAYGROUND_BASE_DIR, with this checkout linked into its venv"
	@echo "playground-link - link this checkout into an existing playground (PROJECT=<project dir>)"
	@echo "linkcli - point the \`djangorocket\` command on PATH at this checkout"

# Run tests
test:
	@echo "${LIGHT_CYAN}Running tests...${NO_COLOR}"
	pytest

# Run end-to-end tests (bakes the template, builds a venv, boots the project)
test-e2e:
	@echo "${LIGHT_CYAN}Running end-to-end tests...${NO_COLOR}"
	pytest --run-e2e -m e2e

# Scaffold a throwaway project (via `djangorocket init`) for manual local
# testing, with $(DJANGOROCKET_SRC_DIR) installed in editable mode both into the
# new project's virtualenv and as the `djangorocket` on PATH -- so the command
# typed inside the playground is the local source, not a release off PATH. Set
# PLAYGROUND_BASE_DIR in .env (see .env.example) to choose where it lands.
playground:
	@echo "${LIGHT_CYAN}Scaffolding a playground project in $(PLAYGROUND_BASE_DIR)...${NO_COLOR}"
	@$(PYTHON) tools/playground.py \
		--source-dir "$(DJANGOROCKET_SRC_DIR)" \
		--base-dir "$(PLAYGROUND_BASE_DIR)" \
		--python "$(PLAYGROUND_PYTHON)" $(LINK_CLI_FLAG)

# Link $(DJANGOROCKET_SRC_DIR) into a playground that already exists, e.g. one
# scaffolded before `make playground` started doing it: make playground-link
# PROJECT=~/playground/my-project
playground-link:
	@if [ -z "$(PROJECT)" ]; then \
		echo "PROJECT is not set. Usage: make playground-link PROJECT=<project dir>"; \
		exit 1; \
	fi
	@echo "${LIGHT_CYAN}Linking $(DJANGOROCKET_SRC_DIR) into $(PROJECT)...${NO_COLOR}"
	@$(PYTHON) tools/playground.py \
		--source-dir "$(DJANGOROCKET_SRC_DIR)" \
		--project-dir "$(PROJECT)" \
		--python "$(PLAYGROUND_PYTHON)" $(LINK_CLI_FLAG)

# Point the `djangorocket` on PATH at $(DJANGOROCKET_SRC_DIR), without touching
# any playground project. Run this after switching DJANGOROCKET_SRC_DIR to
# another checkout, or if a release ever shadows the local build again.
linkcli:
	@echo "${LIGHT_CYAN}Linking the djangorocket command to $(DJANGOROCKET_SRC_DIR)...${NO_COLOR}"
	@$(PYTHON) tools/playground.py \
		--source-dir "$(DJANGOROCKET_SRC_DIR)" \
		--cli-only

# Rebuild the <name>.zip next to each template directory. `djangorocket add`
# renders those zips rather than the directories (see djangorocket/components.py)
# and they are build artifacts, so refreshing them is what makes a UI template
# edit show up in a playground with this checkout linked. The playground targets
# above do it for you; run this after editing a template to test again.
ziptemplates:
	@echo "${LIGHT_CYAN}Zipping templates...${NO_COLOR}"
	$(PYTHON) tools/zip_templates.py

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
	djlint "$(TEMPLATES_DIR)" --extension=html --lint

# Format templates code
formattemplates:
	@echo "${LIGHT_CYAN}Formatting Django HTML code...${NO_COLOR}"
	djlint "$(TEMPLATES_DIR)" --extension=html --reformat
