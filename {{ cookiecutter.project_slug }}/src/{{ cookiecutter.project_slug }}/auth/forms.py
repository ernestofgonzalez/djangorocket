from django import forms
from django.conf import settings


class UpdateUserForm(forms.Form):
    template_name = "auth/forms/update_user_form.html"
    name = forms.CharField(
        max_length=settings.AUTH_USER_NAME_MAX_LENGTH,
        error_messages={"required": "Es necesario que indiques tu nombre."},
        help_text="Tu nombre completo",
        widget=forms.TextInput(attrs={"placeholder": "Julia Garcia"}),
    )


class UpdatePasswordForm(forms.Form):
    template_name = "auth/forms/update_password_form.html"
    password = forms.CharField(
        error_messages={
            "required": "Es necesario que indiques tu actual password.",
        },
    )
    new_password = forms.CharField(
        error_messages={
            "required": "Es necesario que indiques un nuevo password.",
        },
    )
    new_password_confirm = forms.CharField(
        error_messages={
            "required": "Es necesario que confirmes tu nuevo password.",
        },
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")

        if new_password != new_password_confirm:
            raise forms.ValidationError(
                "Tu nueva password y la confirmación no coinciden."
            )


class LoginForm(forms.Form):
    template_name = "auth/forms/login_form.html"
    email = forms.EmailField(
        error_messages={"required": "Es necesario que indiques tu correo electrónico."}
    )
    password = forms.CharField(
        error_messages={"required": "Es necesario que indiques tu password."}
    )


class RegisterForm(forms.Form):
    template_name = "auth/forms/register_form.html"
    name = forms.CharField(
        max_length=settings.AUTH_USER_NAME_MAX_LENGTH,
        error_messages={"required": "Es necesario que indiques tu nombre."},
        widget=forms.TextInput(attrs={"placeholder": "Julia Garcia"}),
    )
    email = forms.EmailField(
        error_messages={"required": "Es necesario que indiques tu correo electrónico."},
        widget=forms.EmailInput(attrs={"placeholder": "ejemplo: julia@tablas.com"}),
    )
    password = forms.CharField(
        min_length=8,
        error_messages={
            "required": "Es necesario que indiques tu password.",
            "min_length": "Tu password debe tener al menos 8 caracteres.",
        },
    )

    terms = forms.BooleanField(
        widget=forms.CheckboxInput(),
        error_messages={
            "required": "Debes aceptar los términos y condiciones para poder empezar.",
        },
    )
