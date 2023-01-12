from django.urls import path

from barbecue_jam.billing import views

app_name = "barbecue_jam-billing"

urlpatterns = [
    path("settings/billing/", views.billing_settings_view, name="billing-settings"),
    path(
        "billing/subscribe-checkout/create/",
        views.create_subscribe_checkout_view,
        name="create-subscribe-checkout",
    ),
    path(
        "billing/cancel-subscription/",
        views.cancel_subscription_view,
        name="cancel-subscription",
    ),
    path(
        "billing/reactivate-subscription/",
        views.reactivate_subscription_view,
        name="reactivate-subscription",
    ),
    path("billing/stripe/webhook/", views.stripe_webhook_view, name="stripe-webhook"),
]
