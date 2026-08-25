from django.conf import settings
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import BaseHasAPIKey


class AllowAnyInDebug(BasePermission):
    def has_permission(self, request, view):
        if settings.DEBUG:
            return True
        return False


class IsAdminUserAndReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            return False

        return request.user and request.user.is_staff


class IsConsumerAuthenticated(BaseHasAPIKey):
    model = APIKey
