"""Cookiecutter post-generation hook for the base project template.

Runs automatically after ``djangorocket init`` renders the project (e.g. via
``make playground``). Cookiecutter executes it with the working directory set to
the freshly generated project root, so it seeds a ready-to-run ``.env`` (fresh
SECRET_KEY plus throwaway Postgres credentials) that lets the project boot
locally without any manual setup.

Kept dependency-free on purpose: ``djangorocket`` only depends on ``click`` and
``cookiecutter``, so this hook must not import Django -- it may not be installed
in the environment running ``init``. SECRET_KEY generation therefore mirrors
Django's ``get_random_secret_key`` (50 characters from the same alphabet)
instead of calling it.
"""

import secrets
from uuid import uuid4

# Same alphabet and length as django.core.management.utils.get_random_secret_key.
SECRET_KEY_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"


def generate_secret_key():
    return "".join(secrets.choice(SECRET_KEY_CHARS) for _ in range(50))


def main():
    postgres_password = uuid4().hex
    postgres_db = uuid4().hex

    with open(".env", "w") as file:
        file.writelines(
            s + "\n"
            for s in [
                "# Django",
                'SECRET_KEY="{0}"'.format(generate_secret_key()),
                "DEBUG=True",
                "SECURE_SSL_REDIRECT=False",
                'ALLOWED_HOSTS=["*"]',
                "CORS_ORIGIN_ALLOW_ALL=True",
                "CORS_ORIGIN_WHITELIST=[]",
                'INTERNAL_IPS=["127.0.0.1"]',
                "",
                "# Databases",
                "DATABASE_URL=postgresql://postgres:{0}@localhost:5432/{1}".format(
                    postgres_password, postgres_db
                ),
                "POSTGRES_PASSWORD={0}".format(postgres_password),
                "POSTGRES_DB={0}".format(postgres_db),
                "",
                "# Celery",
                'CELERY_BROKER_URL="redis://localhost/"',
                'CELERY_ACCEPT_CONTENT=["json"]',
                "",
                "# Google",
                "GOOGLE_OAUTH_CLIENT_ID=",
                "GOOGLE_OAUTH_CLIENT_SECRET=",
                "",
                "# Stripe",
                "STRIPE_PUBLISHABLE_KEY=",
                "STRIPE_SECRET_KEY=",
                "STRIPE_WEBHOOK_SECRET=",
                "STRIPE_PRICE_ID=",
                "",
                "# Heroku ",
                "PORT=8000",
            ]
        )


if __name__ == "__main__":
    main()
