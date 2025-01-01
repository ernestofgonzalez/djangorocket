import json
import os
from pathlib import Path

import boto3
import dj_database_url
import sentry_sdk
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
from opensearchpy import AWSV4SignerAuth, RequestsHttpConnection

# Load environment variables from .env file
load_dotenv(verbose=True)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
if os.environ.get("DEBUG", "False") == "True":
    DEBUG = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = True
if os.environ.get("SECURE_SSL_REDIRECT", "True") == "False":
    SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

ALLOWED_HOSTS = json.loads(os.environ.get("ALLOWED_HOSTS"))
INTERNAL_IPS = json.loads(os.environ.get("INTERNAL_IPS", "[]"))


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "compressor",
    "corsheaders",
    "django_celery_beat",
    "django_countries",
    "djmoney",
    "django_opensearch_dsl",
    "hijack",
    "hijack.contrib.admin",
    "phonenumber_field",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_api_key",
    "storages",
    "tailwind",
    "tailwind_theme",
    "{{ cookiecutter.project_slug }}.auth",
    "{{ cookiecutter.project_slug }}.billing",
    "{{ cookiecutter.project_slug }}.utils",
]

if DEBUG is True:
    INSTALLED_APPS.append("django_browser_reload")
    INSTALLED_APPS.append("debug_toolbar")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "hijack.middleware.HijackUserMiddleware",
]

if DEBUG is True:
    MIDDLEWARE.insert(0, "django_browser_reload.middleware.BrowserReloadMiddleware")
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    MIDDLEWARE.insert(0, "pyinstrument.middleware.ProfilerMiddleware")

ROOT_URLCONF = "{{ cookiecutter.project_slug }}.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "{{ cookiecutter.project_slug }}.context_processors.google_oauth_client_id",
                "{{ cookiecutter.project_slug }}.context_processors.stripe_publishable_key",
            ],
        },
    },
]

WSGI_APPLICATION = "{{ cookiecutter.project_slug }}.wsgi.application"

CORS_ORIGIN_ALLOW_ALL = False
if os.environ.get("CORS_ORIGIN_ALLOW_ALL", "False") == "True":
    CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = json.loads(os.environ.get("CORS_ORIGIN_WHITELIST"))


# Django Rest Framework
# https://www.django-rest-framework.org/

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "{{cookiecutter.project_slug}}.permissions.IsConsumerAuthenticated",
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}

API_KEY_CUSTOM_HEADER = "HTTP_X_API_KEY"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {"default": dj_database_url.config(default=os.environ.get("DATABASE_URL"))}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "{{ cookiecutter.project_slug }}_auth.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_REDIRECT_URL = ""
LOGIN_URL = "/login/"
LOGOUT = ""

# Caches
# https://docs.djangoproject.com/en/4.1/ref/settings/#caches

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-US"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

LANGUAGES = [
    ("en", _("English")),
    ("es", _("Spanish")),
]


# Celery Configuration Options
# https://docs.celeryproject.org

CELERY_BROKER_URL = os.environ.get("REDIS_URL")
CELERY_REDIS_BACKEND_HEALTH_CHECK_INTERVAL = int(
    os.environ.get("CELERY_REDIS_BACKEND_HEALTH_CHECK_INTERVAL", "1000")
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = int(os.environ.get("CELERY_TASK_TIME_LIMIT", "2000"))
CELERY_WORKER_CONCURRENCY = 4
CELERY_WORKER_MAX_MEMORY_PER_CHILD = 50000
CELERY_WORKER_MAX_TASKS_PER_CHILD = 100
CELERY_TIMEZONE = os.environ.get("CELERY_TIMEZONE", "UTC")
CELERY_ENABLE_UTC = True
CELERY_BEAT_SCHEDULER = "django_celery_beta.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
if DEBUG is True:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
STATIC_DIR = os.path.join(BASE_DIR, "static")
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_HOST = os.environ.get("STATIC_HOST")
STATICFILES_DIRS = [
    STATIC_DIR,
]
STATIC_URL = "/static/"


COMPRESS_STORAGE = "compressor.storage.GzipCompressorFileStorage"
COMPRESS_ROOT = os.path.join(BASE_DIR, "staticfiles")
if DEBUG is True:
    COMPRESS_ROOT = os.path.join(BASE_DIR, "static")
COMPRESS_ENABLED = not DEBUG
COMPRESS_OFFLINE = True

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]


# Django Tailwind

TAILWIND_APP_NAME = "tailwind_theme"


# Email configurations
# https://docs.djangoproject.com/en/4.1/topics/email/

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
if os.environ.get("EMAIL_USE_TLS", "True") == "False":
    EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")


# Amazon Web Services configurations
# https://aws.amazon.com

AWS_ACCOUNT_ID = os.environ.get("AWS_ACCOUNT_ID")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_STATIC_BUCKET_NAME = os.environ.get("AWS_STORAGE_STATIC_BUCKET_NAME")
AWS_STORAGE_MEDIA_INPUT_BUCKET_NAME = os.environ.get(
    "AWS_STORAGE_MEDIA_INPUT_BUCKET_NAME"
)
AWS_STORAGE_MEDIA_INPUT_BUCKET_REGION_NAME = os.environ.get(
    "AWS_STORAGE_MEDIA_INPUT_BUCKET_REGION_NAME"
)
AWS_STORAGE_MEDIA_OUTPUT_BUCKET_NAME = os.environ.get(
    "AWS_STORAGE_MEDIA_OUTPUT_BUCKET_NAME"
)
AWS_STORAGE_STATIC_HOST = os.environ.get("AWS_STORAGE_STATIC_HOST", "s3.amazonaws.com")
AWS_STORAGE_MEDIA_INPUT_HOST = os.environ.get(
    "AWS_STORAGE_MEDIA_INPUT_HOST", "s3.amazonaws.com"
)
AWS_STORAGE_MEDIA_OUTPUT_HOST = os.environ.get(
    "AWS_STORAGE_MEDIA_OUTPUT_HOST", "s3.amazonaws.com"
)
AWS_STORAGE_STATIC_DOMAIN = "%s.%s" % (
    AWS_STORAGE_STATIC_BUCKET_NAME,
    AWS_STORAGE_STATIC_HOST,
)
AWS_STORAGE_MEDIA_INPUT_DOMAIN = "%s.%s" % (
    AWS_STORAGE_MEDIA_INPUT_BUCKET_NAME,
    AWS_STORAGE_MEDIA_INPUT_HOST,
)
AWS_STORAGE_MEDIA_OUTPUT_DOMAIN = "%s.%s" % (
    AWS_STORAGE_MEDIA_OUTPUT_BUCKET_NAME,
    AWS_STORAGE_MEDIA_OUTPUT_HOST,
)
AWS_CLOUD_FRONT_DOMAIN_NAME = os.environ.get("AWS_CLOUD_FRONT_DOMAIN_NAME")
AWS_CLOUD_FRONT_PRIVATE_KEY = os.environ.get("AWS_CLOUD_FRONT_PRIVATE_KEY")
AWS_CLOUD_FRONT_KEY_PAIR_ID = os.environ.get("AWS_CLOUD_FRONT_KEY_PAIR_ID")
AWS_OPEN_SEARCH_HOST = os.environ.get("AWS_OPEN_SEARCH_HOST")
AWS_OPEN_SEARCH_REGION_NAME = os.environ.get("AWS_OPEN_SEARCH_REGION_NAME")
AWS_SES_SMTP_USER = os.environ.get("AWS_SES_SMTP_USER")
AWS_SES_SMTP_PASSWORD = os.environ.get("AWS_SES_SMTP_PASSWORD")
AWS_SES_REGION_NAME = os.environ.get("AWS_SES_REGION_NAME")
AWS_SES_REGION_ENDPOINT = os.environ.get("AWS_SES_REGION_ENDPOINT")


# Google

GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", None)
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", None)


# Stripe

STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", None)
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", None)
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", None)
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID", None)


# Mixpanel

MIXPANEL_API_TOKEN = os.environ.get("MIXPANEL_API_TOKEN", None)


# Django Opensearch DSL
# https://django-opensearch-dsl.readthedocs.io/en/latest/

OPENSEARCH_DSL = {
    "default": {
        "hosts": AWS_OPEN_SEARCH_HOST,
        "http_auth": AWSV4SignerAuth(
            boto3.Session(
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            ).get_credentials(),
            AWS_OPEN_SEARCH_REGION_NAME,
            "es",
        ),
        "use_ssl": True,
        "verify_certs": True,
        "connection_class": RequestsHttpConnection,
        "pool_maxsize": 20,
    },
}


# Sentry

SENTRY_DSN = os.environ.get("SENTRY_DSN", None)

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=1.0,
    _experiments={
        "continuous_profiling_auto_start": False,
    },
)


# {{ cookiecutter.project_name }} config

SUBSCRIPTION_TRIAL_PERIOD_DAYS = 14

AUTH_USER_NAME_MAX_LENGTH = int(os.environ.get("AUTH_USER_NAME_MAX_LENGTH", "150"))
