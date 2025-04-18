from django.urls import path

from {{cookiecutter.project_slug}}.search import api_views

app_name = "{{ cookiecutter.project_slug }}-search"

urlpatterns = [
    path(
        "search/",
        api_views.search_view,
        name="search",
    ),
]
