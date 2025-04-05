import builtins
import logging
from decimal import Decimal

from django import template

register = template.Library()

logger = logging.getLogger(__name__)


def valid_numeric(arg):
    if isinstance(arg, (int, float, Decimal)):
        return arg
    try:
        return int(arg)
    except ValueError:
        return float(arg)


def handle_float_decimal_combinations(value, arg, operation):
    if isinstance(value, float) and isinstance(arg, Decimal):
        logger.warning(
            "Unsafe operation: {0!r} {1} {2!r}.".format(value, operation, arg)
        )
        value = Decimal(str(value))
    if isinstance(value, Decimal) and isinstance(arg, float):
        logger.warning(
            "Unsafe operation: {0!r} {1} {2!r}.".format(value, operation, arg)
        )
        arg = Decimal(str(arg))
    return value, arg


@register.filter
def abs(value):
    return builtins.abs(value)


@register.filter
def div(value, arg):
    try:
        nvalue, narg = handle_float_decimal_combinations(
            valid_numeric(value), valid_numeric(arg), "/"
        )
        return nvalue / narg
    except (ValueError, TypeError):
        try:
            return value / arg
        except Exception:
            return ""
