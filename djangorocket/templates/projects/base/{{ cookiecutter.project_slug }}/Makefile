#!/usr/bin/env bash

LIGHT_CYAN=\033[1;36m
NO_COLOR=\033[0m

.PHONY: docs

help:
	@echo "test - run tests quickly with the default Python"
	@echo "pytest - run tests with pytest"
	@echo "coverage - get code coverage report"
	@echo "lint - lint the python code"
	@echo "format - format the python code"
	@echo "linttemplates - lint the Django HTML code"
	@echo "formattemplates - format the Django HTML code"

# Run Django tests
test:
	@echo "${LIGHT_CYAN}Running tests...${NO_COLOR}"
	python3 src/manage.py test --parallel

# Run tests with pytest
pytest: 
	@echo "${LIGHT_CYAN}Running tests with pytest...${NO_COLOR}"
	pytest --durations=1 -n 8

# Get code coverage report
coverage:
	@echo "${LIGHT_CYAN}Running tests and collecting coverage data...${NO_COLOR}"
	pytest --cov=. -n 8
	coverage combine
	@echo "${LIGHT_CYAN}Reporting code coverage data...${NO_COLOR}"
	coverage report
	@echo "${LIGHT_CYAN}Creating HTML report...${NO_COLOR}"
	coverage html
	@echo "${LIGHT_CYAN}Creating coverage badge...${NO_COLOR}"
	@rm ./coverage.svg
	coverage-badge -o coverage.svg

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