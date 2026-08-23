import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "{{ cookiecutter.project_slug }}.settings"
)

application = get_wsgi_application()
