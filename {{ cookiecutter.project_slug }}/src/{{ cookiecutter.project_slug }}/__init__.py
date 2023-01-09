from {{ cookiecutter.project_slug }}.celery import app as celery_app

__all__ = ("celery_app",)
