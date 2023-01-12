from django.contrib import admin

from barbecue_jam.billing.models import StripeCustomer

admin.site.register(StripeCustomer)
