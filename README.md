# djangorocket

[![Django version](https://img.shields.io/badge/django-4.1.4-blue)](https://github.com/ErnestoFGonzalez/djangorocket)
[![Latest Release](https://img.shields.io/github/v/release/ErnestoFGonzalez/djangorocket)](https://github.com/ErnestoFGonzalez/djangorocket/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/ErnestoFGonzalez/djangorocket/blob/main/LICENSE.md)

_Django Rocket is a powerful Django SaaS boilerplate framework designed for indie hackers and SaaS companies that need to quickly launch their paywalled software. It leverages the [Cookiecutter](https://github.com/cookiecutter/cookiecutter) templating engine to generate a project structure with commonly used features such as authentication and billing, saving you time and effort_.

For detailed information on usage and third-party integrations, please refer to the [full documentation](https://djangorocket.com).

## Features

- Subscriptions 
- Stripe payment integration via [stripe-python](https://github.com/stripe/stripe-python)
- Customizable templates with [Tailwind CSS](https://github.com/tailwindlabs/tailwindcss)   (powered by [django-tailwind](https://github.com/timonweb/django-tailwind))
- Custom user model
- Static file serving with [whitenoise](https://github.com/evansd/whitenoise)

## Requirements

Before getting started, make sure to install the following dependencies:
- [cookiecutter](https://github.com/cookiecutter/cookiecutter) 
- [django](https://github.com/django/django). 

You can easily install them using [pip](https://github.com/pypa/pip):

```bash
$ pip install cookiecutter==2.1.1 django==4.1.4
```

> **_NOTE:_** Although Django Rocket works with other versions of Cookiecutter and Django, we recommend using the versions mentioned above, as they are well-tested.

## Usage

To create a new Django Rocket project, simply run the following command in your terminal:

```bash
$ cookiecutter gh:ErnestoFGonzalez/djangorocket
```

You will be prompted to enter your project name and slug, after which the project structure will be generated. Make sure to fill out the `.env` file with the appropriate values for your project.

For comprehensive coverage of features and integrations, check out the [full documentation](https://djangorocket.com).
