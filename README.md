# djangorocket

[![Django version](https://img.shields.io/badge/django-5.2.17-blue)](https://github.com/ErnestoFGonzalez/djangorocket)
[![Latest Release](https://img.shields.io/github/v/release/ErnestoFGonzalez/djangorocket)](https://github.com/ErnestoFGonzalez/djangorocket/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ErnestoFGonzalez/djangorocket/blob/main/LICENSE.md)

_Django Rocket is a powerful Django SaaS boilerplate designed for indie hackers and SaaS companies that need to quickly launch their paywalled software. It leverages the [Cookiecutter](https://github.com/cookiecutter/cookiecutter) templating engine to generate a project structure with commonly used features such as authentication and billing, saving you time and effort_.

For detailed information on usage and third-party integrations, please refer to the [full documentation](https://djangorocket.com).

## Features

- Custom user model with login, registration, and account, email and security settings pages
- Stripe subscriptions via [stripe-python](https://github.com/stripe/stripe-python), with checkout, cancel and reactivate flows and a webhook endpoint
- Customizable templates with [Tailwind CSS](https://github.com/tailwindlabs/tailwindcss) (powered by [django-tailwind](https://github.com/timonweb/django-tailwind))
- A REST API with token and API-key authentication, via [djangorestframework](https://github.com/encode/django-rest-framework)
- Search backed by OpenSearch, and background work with [celery](https://github.com/celery/celery) on Redis
- Postgres and Redis defined in `docker-compose.yml`, on host ports picked free on your machine
- Static file serving with [whitenoise](https://github.com/evansd/whitenoise)

## Installation

Install the CLI with [pip](https://github.com/pypa/pip):

```bash
$ pip install djangorocket
```

Generating and running a project needs:

- **Python 3.10 - 3.14**
- **Docker**, to run the Postgres and Redis services the generated project comes with

## Usage

To create a new Django Rocket project, run the following command in your terminal:

```bash
$ djangorocket init
```

You will be prompted for your project name, after which the project structure will be generated. Scaffolding writes a working `.env` for you — a fresh `SECRET_KEY`, throwaway Postgres credentials and free host ports — so there is nothing to fill in before booting locally.

One command then takes the new project to a running app, creating a virtualenv, installing the dependencies, starting Postgres and Redis, and applying the migrations:

```bash
$ make bootstrap
$ make runserver
```

Each generated project ships a README covering its layout, every `make` target, the Tailwind workflow and what to set when deploying.

### Adding UI templates

To add a UI component to an existing Django Rocket project, run `add` from the project root:

```bash
$ djangorocket add accordion
```

### Using cookiecutter directly

Django Rocket is also usable as a plain Cookiecutter template, without installing the CLI:

```bash
$ pip install cookiecutter==2.1.1
$ cookiecutter gh:ErnestoFGonzalez/djangorocket --directory="djangorocket/templates/projects/base"
```

> **_NOTE:_** Although Django Rocket works with other versions of Cookiecutter, we recommend the version mentioned above, as it is the one that's well-tested.

For comprehensive coverage of features and integrations, check out the [full documentation](https://djangorocket.com).
