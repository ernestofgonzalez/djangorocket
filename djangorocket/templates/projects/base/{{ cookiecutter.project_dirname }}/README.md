# {{ cookiecutter.project_name }}

A Django SaaS application scaffolded with [DjangoRocket](https://djangorocket.com), with
authentication, Stripe subscriptions, a Tailwind frontend and a REST API already wired up.

## Requirements

- **Python 3.10 - 3.14** — `make bootstrap` builds the virtualenv with whatever `python3` is on your `PATH`. `runtime.txt` pins the version used when deploying.
- **Docker** — runs the Postgres and Redis services defined in `docker-compose.yml`

## Getting started

One command does the whole setup: it creates a virtualenv in `.venv`, installs the
dependencies, starts Postgres and Redis, and applies the migrations.

```bash
make bootstrap
```

Then start the server and open <http://127.0.0.1:8000/>:

```bash
make runserver
```

To reach the Django admin at `/admin/`, create an account first:

```bash
.venv/bin/python src/manage.py createsuperuser
```

### Your `.env`

Scaffolding already wrote a working `.env`: a fresh `SECRET_KEY`, throwaway Postgres
credentials, and host ports for Postgres and Redis picked free on this machine (so
several DjangoRocket projects can run side by side). There is nothing to fill in before
booting locally.

That file holds real secrets and is gitignored — keep it that way. `.env.example` lists
every variable `settings.py` reads, which makes it the checklist to work through when you
configure a deployment.

## What's included

| Area | Details |
| --- | --- |
| Authentication | Custom user model in `{{ cookiecutter.project_slug }}.auth`, with login, registration, and account, email and security settings pages |
| Billing | Stripe subscription checkout, cancel and reactivate flows, a webhook endpoint and a billing settings page, in `{{ cookiecutter.project_slug }}.billing` |
| Frontend | Server-rendered Django templates styled with [Tailwind CSS](https://tailwindcss.com/) through `django-tailwind`, served by `whitenoise` |
| API | `djangorestframework` with token and API-key authentication, mounted under `/api/` |
| Search | An OpenSearch-backed search endpoint via `django-opensearch-dsl`, in `{{ cookiecutter.project_slug }}.search` |
| Background work | `celery` with a Redis broker, plus `django-celery-beat` for scheduled tasks |
| Tooling | `django-debug-toolbar` and live reload while `DEBUG=True`; `black`, `isort`, `flake8` and `djlint` for linting |

### Optional integrations

These keys start out blank. The project boots, migrates and passes its test suite without
them, so fill in only what you need:

- `STRIPE_*` — subscription checkout and the billing pages
- `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` — "Sign in with Google"
- `AWS_*` — S3 media storage, SES email and OpenSearch search
- `MIXPANEL_API_TOKEN` — product analytics

## Project layout

```
.
├── requirements/            # dependencies, split by purpose
├── src/
│   ├── {{ cookiecutter.project_slug }}/
│   │   ├── auth/            # custom user model, login, registration, settings pages
│   │   ├── billing/         # Stripe subscriptions and webhooks
│   │   ├── search/          # OpenSearch-backed search API
│   │   ├── utils/           # shared template tags and helpers
│   │   ├── settings.py      # all configuration, read from the environment
│   │   └── urls.py          # URL roots for the project
│   ├── static/              # project-wide static assets
│   ├── tailwind_theme/      # Tailwind theme app and compiled CSS
│   ├── templates/           # base layout and shared components
│   └── manage.py
├── docker-compose.yml       # Postgres and Redis for local development
└── Makefile                 # the commands below
```

## Common tasks

`make help` lists every target.

| Command | What it does |
| --- | --- |
| `make bootstrap` | Full setup from a fresh clone: virtualenv, dependencies, services, migrations |
| `make runserver` | Start the Django development server |
| `make setupdb` / `make setupredis` | Start Postgres / Redis, waiting until it is healthy |
| `make test` | Run the test suite with Django's test runner |
| `make pytest` | Run the test suite with pytest |
| `make coverage` | Run the tests, then write a coverage report and badge |
| `make lint` / `make format` | Check / apply `isort`, `black` and `flake8` |
| `make linttemplates` / `make formattemplates` | Check / apply `djlint` to the Django templates |

Every target reuses the `.venv` that `make bootstrap` created, so there is no virtualenv to
activate by hand.

## Working on the styles

The compiled CSS is committed, so Node is only needed when you change the design:

```bash
.venv/bin/python src/manage.py tailwind install   # once, to install the npm packages
.venv/bin/python src/manage.py tailwind start     # watch and rebuild while you work
```

Build the minified stylesheet with `.venv/bin/python src/manage.py tailwind build`.

## Deploying

The project runs on any host that can serve a Python web process:

- `gunicorn` is included — serve `{{ cookiecutter.project_slug }}.wsgi` from the `src/`
  directory, binding to the `PORT` environment variable
- `whitenoise` serves hashed static files, so run `manage.py collectstatic` and
  `manage.py compress` as part of your build
- set `DEBUG=False`, a strong `SECRET_KEY`, a real `ALLOWED_HOSTS` and
  `SECURE_SSL_REDIRECT=True`
- point `DATABASE_URL` at a managed Postgres instance and `CELERY_BROKER_URL` at a managed
  Redis

## Documentation

DjangoRocket's own documentation, including the third-party integration guides, is at
[djangorocket.com](https://djangorocket.com).
