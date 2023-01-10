from django.conf import settings


def stripe_publishable_key(request):
    return {"stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY}
