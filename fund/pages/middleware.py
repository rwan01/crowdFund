from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .session_utils import get_user_user, get_admin_user

class DualAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Leave request.user alone (Django handles it)
        # Instead, add custom attributes
        request.custom_user = get_user_user(request)
        request.custom_admin = get_admin_user(request)

        # Safety: if request.user is None, set AnonymousUser
        if request.user is None:
            request.user = AnonymousUser()
