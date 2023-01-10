#!/usr/bin/env bash

LIGHT_CYAN=\033[1;36m
NO_COLOR=\033[0m

.PHONY: docs

help:
	@echo "lint - lint the python code"
	@echo "format - format the python code"
	@echo "linttemplates - lint the Django HTML code"
	@echo "formattemplates - format the Django HTML code"

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
