from django.apps import AppConfig


class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "{{ cookiecutter.project_slug }}.search"
    label = "{{ cookiecutter.project_slug }}_search"
