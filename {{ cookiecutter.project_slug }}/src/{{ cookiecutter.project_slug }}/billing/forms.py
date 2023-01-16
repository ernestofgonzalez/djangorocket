from django import forms
from django_countries.fields import CountryField


class UpdateBillingInformationForm(forms.Form):
    template_name = "billing/forms/update_billing_information_form.html"
    name = forms.CharField(
        max_length=255,
        label="Name",
        error_messages={"required": "You need to enter your name."},
        help_text="Your full name",
        widget=forms.TextInput(),
        required=True,
    )
    address_line_1 = forms.CharField(
        max_length=255,
        label="Address",
        help_text="P.O box, company name, c/o",
        widget=forms.TextInput(),
        required=True,
    )
    address_line_2 = forms.CharField(
        max_length=255,
        label="Address line 2",
        help_text="Apartment, suite, unit",
        widget=forms.TextInput(),
    )
    city = forms.CharField(
        max_length=255,
        label="City", 
        widget=forms.TextInput(), 
        required=True
    )
    postal_code = forms.CharField(
        max_length=255,
        label="Postal/Zip code",
        widget=forms.TextInput(),
    )
    country = CountryField().formfield(
        label="Country",
        widget=forms.Select(attrs={"placeholder": "Choose your country"})
    )
