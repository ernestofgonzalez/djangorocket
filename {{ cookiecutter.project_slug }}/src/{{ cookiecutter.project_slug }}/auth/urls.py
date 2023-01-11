from django.urls import path
from {{cookiecutter.project_slug}}.auth import views

app_name = "{{ cookiecutter.project_slug }}-auth"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("settings/account/", views.account_settings_view, name="account-settings"),
    path("settings/email/", views.email_settings_view, name="email-settings"),
    path("settings/security/", views.security_settings_view, name="security-settings"),
]
