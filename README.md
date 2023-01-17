# djangorocket

[![Django version](https://img.shields.io/badge/django-4.1.4-blue)](https://github.com/ErnestoFGonzalez/djangorocket)
[![Latest Release](https://img.shields.io/github/v/release/ErnestoFGonzalez/djangorocket)](https://github.com/ErnestoFGonzalez/djangorocket/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ErnestoFGonzalez/djangorocket/blob/main/LICENSE.md)

_Django Rocket is a Django SaaS boilerplate framework powered by [Cookiecutter](https://github.com/cookiecutter/cookiecutter)_.

Django Rocket is aimed at indie hackers or SaaS companies that want to launch paywalled software __fast__. It saves you tens of hours in tedious work in authentication and billing.

For detailed information on usage and third-party integrations check the [full documentation](https://ernestofgonzalez.github.io/djangorocket/).

## Features

- Subscriptions 
- Billing with [Stripe](https://github.com/stripe/stripe-python)
- Style your templates with [Tailwind CSS](https://github.com/tailwindlabs/tailwindcss) (uses [django-tailwind](https://github.com/timonweb/django-tailwind))
- Custom user model
- Serve your own static files with [whitenoise](https://github.com/evansd/whitenoise)

## Requirements

To get started, you need to install the dependencies
- [cookiecutter](https://github.com/cookiecutter/cookiecutter) 
- [django](https://github.com/django/django). 

You can install them via [pip](https://github.com/pypa/pip)

```bash
$ pip install cookiecutter==2.1.1 django==4.1.4
```

or you can use the requirements file

```bash
$ pip install -r requirements/requirements.txt
```

> **_NOTE:_** Django Rocket works with other versions of Cookiecutter and Django, but as it lacks extensive test coverage, for now it's better to stick to the mentioned versions.

## Usage

Open your terminal and use [cookiecutter](https://github.com/cookiecutter/cookiecutter) command to create your project 

```bash
$ cookiecutter gh:ErnestoFGonzalez/djangorocket
```

You'll be prompted to enter your project name and project slug. You'll see something like this:
```bash
project_name [My Project]: Soup Shop
project_slug [soup_shop]: soup_shop
```

You should see your project directory. All it's left to doo is to fill to create a `.env` file. Make sure you enter a value for all the keys in the `.env.example` file.

Check out the [full documentation](https://ernestofgonzalez.github.io/djangorocket/) for comprehensive coverage of features and integrations.
