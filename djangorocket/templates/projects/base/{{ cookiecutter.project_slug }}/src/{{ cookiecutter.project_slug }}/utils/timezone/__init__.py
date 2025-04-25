from django.utils.timezone import now as django_utils_timezone_now


def now():
    return django_utils_timezone_now()
