import stripe
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.functional import cached_property
from phonenumber_field.modelfields import PhoneNumberField
from {{cookiecutter.project_slug}}.utils import default_uuid


class User(AbstractUser):
    uuid = models.CharField(
        default=default_uuid, editable=False, unique=True, max_length=255
    )

    username = None
    first_name = None
    last_name = None

    name = models.CharField(
        null=False, blank=False, max_length=settings.AUTH_USER_NAME_MAX_LENGTH
    )

    phone_number = PhoneNumberField(unique=True, null=True, blank=False)

    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)

    google_id = models.CharField(
        null=True, blank=False, max_length=255,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "name",
    ]

    class Meta:
        ordering = ["-date_joined"]

    @cached_property
    def default_payment_method(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer = stripe.Customer.retrieve(
            self.stripe_customer.stripe_customer_id,
            expand=["invoice_settings.default_payment_method"],
        )
        return customer["invoice_settings"]["default_payment_method"]

    @cached_property
    def subscription(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        subscription = stripe.Subscription.retrieve(
            self.stripe_customer.stripe_subscription_id,
            expand=["default_payment_method"],
        )
        return subscription
