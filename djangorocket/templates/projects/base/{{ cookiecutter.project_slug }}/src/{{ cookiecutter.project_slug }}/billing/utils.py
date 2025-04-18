import stripe
from django.conf import settings
from {{cookiecutter.project_slug}}.model_loaders import get_stripe_customer_model


def create_subscription_for_user(user, trial_period_days):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    customer = stripe.Customer.create(
        email=user.email,
        name=user.name,
    )
    susbcription = stripe.Subscription.create(
        customer=customer.id,
        items=[{"price": settings.STRIPE_PRICE_ID}],
        trial_period_days=trial_period_days,
    )

    StripeCustomer = get_stripe_customer_model()
    StripeCustomer.objects.create(
        user=user,
        stripe_customer_id=customer.id,
        stripe_subscription_id=susbcription.id,
    )