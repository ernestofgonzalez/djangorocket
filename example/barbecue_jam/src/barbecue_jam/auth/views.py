from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from barbecue_jam.auth.forms import (
    LoginForm,
    RegisterForm,
    UpdatePasswordForm,
    UpdateUserForm,
)


@never_cache
@require_http_methods(["GET", "POST"])
@login_required
def account_settings_view(request):
    context = {
        "current_tab": "account",
    }

    form = UpdateUserForm(
        request.POST
        or {
            "name": request.user.name,
        },
        initial={
            "name": request.user.name,
        },
    )
    context["form"] = form

    if request.method == "POST":
        if form.is_valid():
            if form.has_changed():
                for attr in form.changed_data:
                    setattr(request.user, attr, form.cleaned_data[attr])
                request.user.save()

            return redirect("barbecue_jam-auth:account-settings")

    return render(request, "auth/pages/account_settings.html", context)


@never_cache
@require_GET
@login_required
def email_settings_view(request):
    context = {
        "current_tab": "email",
    }

    return render(request, "auth/pages/email_settings.html", context)


def security_settings_view(request):
    context = {
        "current_tab": "security",
    }

    form = UpdatePasswordForm(request.POST or None)
    context["form"] = form

    if request.method == "POST":
        if form.is_valid():
            if request.user.check_password(form.cleaned_data["password"]):
                request.user.set_password(form.cleaned_data["new_password"])
                request.user.save()

                return redirect("barbecue_jam-auth:security-settings")
            else:
                form.add_error(None, "Password incorrecto.")

    return render(request, "auth/pages/security_settings.html", context)


@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    context = {}

    form = LoginForm(request.POST or None)
    context["form"] = form

    if request.method == "POST":
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data.get("email", None),
                password=form.cleaned_data.get("password", None),
            )
            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                form.add_error(None, "Correo electrónico o password incorrectos.")

    return render(request, "auth/pages/login.html", context)


@never_cache
@require_http_methods(["GET", "POST"])
def register_view(request):
    context = {}

    form = RegisterForm(request.POST or None)
    context["form"] = form

    if request.method == "POST":
        if form.is_valid():
            try:
                user = get_user_model().objects.create(
                    name=form.cleaned_data.get("name", None),
                    email=form.cleaned_data.get("email", None),
                )

                user.set_password(form.cleaned_data["password"])
                user.save()

                login(request, user)
                return redirect("index")
            except IntegrityError as e:
                form.add_error(
                    None, "Este correo electrónico ya está asociado a una cuenta."
                )

    return render(request, "auth/pages/register.html", context)


@never_cache
@require_POST
@login_required(redirect_field_name=None)
def logout_view(request):
    logout(request)
    return redirect("index")
