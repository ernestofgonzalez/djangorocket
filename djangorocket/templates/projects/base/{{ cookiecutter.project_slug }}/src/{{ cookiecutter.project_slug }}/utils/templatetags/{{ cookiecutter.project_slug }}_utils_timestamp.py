from datetime import datetime

from django import template

register = template.Library()


@register.filter
def timestamp_to_datetime(value):
    return datetime.fromtimestamp(value)
