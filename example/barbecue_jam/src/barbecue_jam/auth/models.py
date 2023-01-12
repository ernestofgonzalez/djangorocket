from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from barbecue_jam.utils import default_uuid


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

    email = models.EmailField(max_length=254, unique=True, null=False, blank=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "name",
    ]

    class Meta:
        ordering = ["-date_joined"]
