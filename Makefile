#!/usr/bin/env bash

LIGHT_CYAN=\033[1;36m
NO_COLOR=\033[0m

# Load developer-local settings (e.g. PLAYGROUND_BASE_DIR) from .env if present.
ifneq (,$(wildcard ./.env))
include .env
export
endif

.PHONY: docs test test-e2e playground

help:
	@echo "test - run tests (fast; e2e tests are skipped)"
	@echo "test-e2e - run the end-to-end tests (slow; bakes and boots a generated project)"
	@echo "lint - lint the python code"
	@echo "format - format the python code"
	@echo "linttemplates - lint the Django HTML code"
	@echo "formattemplates - format the Django HTML code"
	@echo "playground - scaffold a throwaway project in \$$PLAYGROUND_BASE_DIR for manual testing"

# Run tests
test:
	@echo "${LIGHT_CYAN}Running tests...${NO_COLOR}"
	pytest

# Run end-to-end tests (bakes the template, builds a venv, boots the project)
test-e2e:
	@echo "${LIGHT_CYAN}Running end-to-end tests...${NO_COLOR}"
	pytest --run-e2e -m e2e

# Scaffold a throwaway project (via `djangorocket init`) for manual local testing.
# Set PLAYGROUND_BASE_DIR in .env (see .env.example) to choose where it lands.
playground:
	@if [ -z "$(PLAYGROUND_BASE_DIR)" ]; then \
		echo "PLAYGROUND_BASE_DIR is not set. Add it to .env (see .env.example)."; \
		exit 1; \
	fi
	@echo "${LIGHT_CYAN}Scaffolding a playground project in $(PLAYGROUND_BASE_DIR)...${NO_COLOR}"
	@mkdir -p "$(PLAYGROUND_BASE_DIR)"
	@cd "$(PLAYGROUND_BASE_DIR)" && djangorocket init

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
	djlint "{{ cookiecutter.project_slug }}/src/" --extension=html --lint

# Format templates code
formattemplates:
	@echo "${LIGHT_CYAN}Linting Django HTML code...${NO_COLOR}"
	djlint "{{ cookiecutter.project_slug }}/src/" --extension=html --reformat
