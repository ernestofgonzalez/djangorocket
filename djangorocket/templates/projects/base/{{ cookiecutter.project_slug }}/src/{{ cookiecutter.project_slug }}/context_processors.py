from django.conf import settings


def google_oauth_client_id(request):
    return {"google_oauth_client_id": settings.GOOGLE_OAUTH_CLIENT_ID}


def stripe_publishable_key(request):
    return {"stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY}
