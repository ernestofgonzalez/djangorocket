from django import forms
from django.conf import settings


class UpdateUserForm(forms.Form):
    template_name = "auth/forms/update_user_form.html"
    name = forms.CharField(
        max_length=settings.AUTH_USER_NAME_MAX_LENGTH,
        error_messages={"required": "You need to enter your name."},
        help_text="Your full name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your name."}),
    )


class UpdatePasswordForm(forms.Form):
    template_name = "auth/forms/update_password_form.html"
    password = forms.CharField(
        label="Current password",
        error_messages={
            "required": "You need to enter your current password.",
        },
    )
    new_password = forms.CharField(
        label="New password",
        error_messages={
            "required": "You need to enter a new password.",
        },
    )
    new_password_confirm = forms.CharField(
        label="Confirm new password",
        error_messages={
            "required": "You need to confirm your new password.",
        },
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")

        if new_password != new_password_confirm:
            raise forms.ValidationError("The new passwords entered don't match.")


class LoginForm(forms.Form):
    template_name = "auth/forms/login_form.html"
    email = forms.EmailField(
        label="Email address",
        error_messages={"required": "You need to enter your email."},
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email address."}),
    )
    password = forms.CharField(
        label="Password",
        error_messages={"required": "You need to enter your password."},
        widget=forms.TextInput(
            attrs={"placeholder": "Enter your password."},
        ),
    )


class RegisterForm(forms.Form):
    template_name = "auth/forms/register_form.html"
    name = forms.CharField(
        max_length=settings.AUTH_USER_NAME_MAX_LENGTH,
        label="Full name",
        error_messages={"required": "You need to enter your name."},
        widget=forms.TextInput(attrs={"placeholder": "Enter your name."}),
    )
    email = forms.EmailField(
        label="Email address",
        error_messages={"required": "You need to enter your email address."},
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email address."}),
    )
    password = forms.CharField(
        min_length=8,
        label="Password",
        error_messages={
            "required": "You need to enter a password.",
            "min_length": "Your password must have at least 8 characters.",
        },
        widget=forms.TextInput(
            attrs={"placeholder": "Create a password."},
        ),
    )

    terms = forms.BooleanField(
        widget=forms.CheckboxInput(),
        error_messages={
            "required": "You need to accept the Terms and Conditions.",
        },
    )
