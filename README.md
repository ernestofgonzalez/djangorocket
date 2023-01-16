# djangorocket
_A Django SaaS boilerplate_

Django Rocket is a Django SaaS boilerplate framework powered by [Cookiecutter](https://github.com/cookiecutter/cookiecutter)

## Features

- Subscriptions
- Billing with Stripe
- Tailwind CSS for templates using [django-tailwind](https://github.com/timonweb/django-tailwind)
- Customer user model
- Static files with [whitenoise](https://github.com/evansd/whitenoise)

## Installation

To get started, you need to install [cookiecutter](https://github.com/cookiecutter/cookiecutter). I'd recommend doing so using [pip](https://pypi.org/project/cookiecutter/).

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

## Documentation and code coverage

I initially created Django Rocket to jumstart my personal projects without having to copy-paste or rewrite the same code over and over, so I'll be adding documentation and increasing code coverage in the next few days. 





