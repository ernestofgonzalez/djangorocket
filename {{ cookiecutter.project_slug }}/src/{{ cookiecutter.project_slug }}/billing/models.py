from django.db import models


class StripeCustomer(models.Model):
    user = models.OneToOneField(
        "{{ cookiecutter.project_slug }}_auth.User", related_name="stripe_customer", on_delete=models.CASCADE
    )
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
