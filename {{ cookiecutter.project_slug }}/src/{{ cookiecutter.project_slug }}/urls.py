from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from {{cookiecutter.project_slug}} import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index_view, name="index"),
    path("", include("{{ cookiecutter.project_slug }}.auth.urls")),
    path("", include("{{ cookiecutter.project_slug }}.billing.urls")),
]

if settings.DEBUG is True:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
        path("__reload__/", include("django_browser_reload.urls")),
    ]
