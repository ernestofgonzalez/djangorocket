from uuid import uuid4
from django.core.management.utils import get_random_secret_key


def main():
    postgres_password = uuid4().hex
    postgres_db = uuid4().hex

    with open(".env", "w") as file:
        file.writelines(
            s + "\n"
            for s in [
                "# Django",
                'SECRET_KEY="{0}"'.format(get_random_secret_key()),
                "DEBUG=True",
                "SECURE_SSL_REDIRECT=False",
                'ALLOWED_HOSTS=["*"]',
                "CORS_ORIGIN_ALLOW_ALL=True",
                "CORS_ORIGIN_WHITELIST=[]",
                'INTERNAL_IPS=["127.0.0.1"]',
                "",
                "# Databases",
                "DATABASE_URL=postgresql://postgres:{0}@localhost:5432/{1}".format(
                    postgres_password,
                    postgres_db
                ),
                "POSTGRES_PASSWORD={0}".format(postgres_password),
                "POSTGRES_DB={0}".format(postgres_db),
                "",
                "# Celery",
                'CELERY_BROKER_URL="redis://localhost/"',
                'CELERY_ACCEPT_CONTENT=["json"]',
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
