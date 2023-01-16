from django.contrib import admin

from {{ cookiecutter.project_slug }}.billing.models import StripeCustomer

admin.site.register(StripeCustomer)
