from django.conf import settings
from google.auth.transport import requests
from google.oauth2 import id_token


def validate_google_id_token(request):
    csrf_token_cookie = request.COOKIES.get("g_csrf_token", None)
    if not csrf_token_cookie:
        raise Exception("No CSRF token in Cookie.")

    csrf_token_body = request.POST.get("g_csrf_token", None)
    if not csrf_token_body:
        raise Exception("No CSRF token in post body.")
    if csrf_token_cookie != csrf_token_body:
        raise Exception("Failed to verify double submit cookie.")

    id_token_body = request.POST.get("credential", None)
    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_body, requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID
        )
    except ValueError:
        raise Exception("Invalid token.")

    return idinfo
